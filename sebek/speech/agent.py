"""Speech agent for SEBEK - multiprocess microphone listener.

Captures audio from microphone, runs offline speech recognition (Vosk),
and posts transcriptions to SEBEK API endpoint.

Usage:
    python -m sebek.speech.agent --model /path/to/vosk-model

Systemd service unit available in repo: sebek-speech.service
"""

import argparse
import json
import queue
import sys
import time
import uuid
import wave
from multiprocessing import Event, Process, Queue
from pathlib import Path
from typing import Optional

import requests

from sebek.config import Config
from sebek.utils.logging import get_logger, setup_root_logger
from sebek.utils.errors import SpeechError
from sebek.speech.recognizer import (
    VoskRecognizer,
    TextToSpeech,
    save_audio_to_wav,
    SpeechRecognitionResult,
)

logger = get_logger(__name__)

# Audio parameters
SAMPLE_RATE = Config.speech.sample_rate
CHANNELS = Config.speech.channels
BLOCKSIZE = Config.speech.blocksize

# Try to import audio capture
try:
    import sounddevice as sd
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


def post_result_to_sebek(
    result: SpeechRecognitionResult,
    url: Optional[str] = None,
    max_retries: int = 3,
    backoff: float = 1.0,
    source: str = "mic",
) -> Optional[requests.Response]:
    """Post speech recognition result to SEBEK API.

    Args:
        result: Speech recognition result to post.
        url: SEBEK API endpoint. Uses config default if None.
        max_retries: Number of retry attempts.
        backoff: Backoff multiplier between retries (seconds).
        source: Observation source label (e.g., "mic", "sim").

    Returns:
        requests.Response: API response, or None if all retries failed.
    """
    url = url or Config.ollama.api_observe_endpoint
    headers = {"Content-Type": "application/json"}

    payload = {
        "type": "speech",
        "source": source,
        "text": result.text,
        "confidence": result.confidence,
        "words": result.words,
        "vosk": result.vosk_result,
        "metadata": {
            "audio_path": str(result.audio_path) if result.audio_path else None,
            "timestamp": result.timestamp,
        },
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            logger.info(f"Posted to SEBEK: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                wait_time = backoff * attempt
                logger.warning(
                    f"Failed to post to SEBEK (attempt {attempt}/{max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to post to SEBEK after {max_retries} attempts: {e}")

    return None


def recorder_worker(
    audio_queue: Queue,
    stop_event: Event,
    device: Optional[int] = None,
) -> None:
    """Worker process: capture microphone audio and queue it.

    Args:
        audio_queue: Queue to put audio chunks into.
        stop_event: Event to signal shutdown.
        device: Audio device index, or None for default.
    """
    if not HAS_AUDIO:
        logger.error("sounddevice not available - cannot record audio")
        stop_event.set()
        return

    try:
        def audio_callback(indata, frames, time_info, status):
            """Callback for audio stream."""
            if status:
                logger.warning(f"Audio stream status: {status}")
            audio_queue.put(indata.copy())

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=int(BLOCKSIZE / 2),
            dtype="int16",
            channels=CHANNELS,
            device=device,
            callback=audio_callback,
        ):
            logger.info("Audio recorder started")
            while not stop_event.is_set():
                time.sleep(0.1)

    except Exception as e:
        logger.exception(f"Recorder error: {e}")
        stop_event.set()


def recognizer_worker(
    audio_queue: Queue,
    stop_event: Event,
    model_path: Path,
    sebek_url: Optional[str] = None,
    persist_dir: Optional[Path] = None,
) -> None:
    """Worker process: recognize speech and post results.

    Args:
        audio_queue: Queue to get audio chunks from.
        stop_event: Event to signal shutdown.
        model_path: Path to Vosk model directory.
        sebek_url: SEBEK API endpoint.
        persist_dir: Directory to save audio snippets.
    """
    sebek_url = sebek_url or Config.ollama.api_observe_endpoint
    persist_dir = persist_dir or Config.speech.persist_dir

    try:
        # Initialize recognizer
        recognizer = VoskRecognizer(model_path)
        bytes_buffer = bytearray()

        logger.info("Recognizer worker started")

        while not stop_event.is_set():
            try:
                # Get audio chunk from queue with timeout
                chunk = audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            # Convert numpy array to bytes if needed
            if isinstance(chunk, bytes):
                raw = chunk
            else:
                raw = chunk.tobytes()

            bytes_buffer.extend(raw)

            # Check if we have a complete utterance
            if recognizer.accept_waveform(raw):
                try:
                    result = recognizer.get_result()

                    if result.text:
                        # Save audio snippet
                        try:
                            persist_dir.mkdir(parents=True, exist_ok=True)
                            audio_file = (
                                persist_dir
                                / f"speech_{result.timestamp}_{uuid.uuid4().hex[:8]}.wav"
                            )
                            save_audio_to_wav(audio_file, bytes(bytes_buffer))
                            result.audio_path = audio_file
                        except Exception as e:
                            logger.warning(f"Failed to save audio: {e}")

                        # Post to SEBEK
                        post_result_to_sebek(result, sebek_url)

                    # Reset for next utterance
                    bytes_buffer = bytearray()
                    recognizer.reset()

                except SpeechError as e:
                    logger.error(f"Speech recognition error: {e}")
                    bytes_buffer = bytearray()
                    recognizer.reset()

    except SpeechError as e:
        logger.error(f"Recognizer initialization failed: {e}")
        stop_event.set()
    except Exception as e:
        logger.exception(f"Recognizer worker error: {e}")
        stop_event.set()


def sim_recognize_file(
    wav_file: Path,
    model_path: Path,
    sebek_url: Optional[str] = None,
    persist_dir: Optional[Path] = None,
) -> int:
    """Run speech recognition by replaying a WAV file."""
    sebek_url = sebek_url or Config.ollama.api_observe_endpoint
    persist_dir = persist_dir or Config.speech.persist_dir

    if not wav_file.exists():
        logger.error(f"Simulator file not found: {wav_file}")
        return 1

    try:
        recognizer = VoskRecognizer(model_path)
        bytes_buffer = bytearray()

        with wave.open(str(wav_file), "rb") as wf:
            if wf.getnchannels() != CHANNELS or wf.getframerate() != SAMPLE_RATE:
                logger.warning(
                    "Simulator WAV format differs from configured sample rate/channels"
                )

            while True:
                chunk = wf.readframes(4000)
                if not chunk:
                    break

                bytes_buffer.extend(chunk)

                if recognizer.accept_waveform(chunk):
                    result = recognizer.get_result()
                    if result.text:
                        try:
                            persist_dir.mkdir(parents=True, exist_ok=True)
                            audio_file = (
                                persist_dir
                                / f"sim_speech_{result.timestamp}_{uuid.uuid4().hex[:8]}.wav"
                            )
                            save_audio_to_wav(audio_file, bytes(bytes_buffer))
                            result.audio_path = audio_file
                        except Exception as e:
                            logger.warning(f"Failed to save simulator audio: {e}")

                        post_result_to_sebek(result, sebek_url, source="sim")

                    bytes_buffer = bytearray()
                    recognizer.reset()

        try:
            final_result = json.loads(recognizer.recognizer.FinalResult())
        except Exception:
            final_result = {"text": ""}

        final_text = final_result.get("text", "").strip()
        final_words = final_result.get("result", [])
        if final_text:
            confidences = [
                word.get("conf")
                for word in final_words
                if isinstance(word.get("conf"), (int, float))
            ]
            avg_confidence = (
                float(sum(confidences) / len(confidences)) if confidences else None
            )
            result = SpeechRecognitionResult(
                text=final_text,
                confidence=avg_confidence,
                words=final_words,
                vosk_result=final_result,
                timestamp=time.strftime("%Y%m%d_%H%M%S"),
            )
            if bytes_buffer:
                try:
                    persist_dir.mkdir(parents=True, exist_ok=True)
                    audio_file = (
                        persist_dir
                        / f"sim_speech_final_{result.timestamp}_{uuid.uuid4().hex[:8]}.wav"
                    )
                    save_audio_to_wav(audio_file, bytes(bytes_buffer))
                    result.audio_path = audio_file
                except Exception as e:
                    logger.warning(f"Failed to save simulator final audio: {e}")
            post_result_to_sebek(result, sebek_url, source="sim")

        logger.info("SEBEK speech simulator run complete")
        return 0

    except SpeechError as e:
        logger.error(f"Simulator recognition error: {e}")
        return 1
    except (wave.Error, OSError) as e:
        logger.error(f"Invalid simulator WAV file {wav_file}: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Simulator execution failed: {e}")
        return 1


def main() -> int:
    """Main entry point for speech agent.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="SEBEK Speech Agent - Offline ASR with Vosk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Config.speech.vosk_model_path,
        help="Path to Vosk model directory",
    )
    parser.add_argument(
        "--sebek-url",
        type=str,
        default=Config.ollama.api_observe_endpoint,
        help="SEBEK API endpoint for posting observations",
    )
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=Config.speech.persist_dir,
        help="Directory to save audio snippets",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Audio device index (use sounddevice.query_devices() to list)",
    )
    parser.add_argument(
        "--no-tts",
        action="store_true",
        help="Disable text-to-speech feedback",
    )
    parser.add_argument(
        "--sim-file",
        type=Path,
        default=None,
        help="Replay WAV file in simulator mode instead of live microphone capture",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_root_logger()

    try:
        # Validate requirements
        if not args.model.exists():
            logger.error(
                f"Vosk model not found at {args.model}. "
                "Download from https://alphacephei.com/vosk/models"
            )
            return 1

        if args.sim_file is not None:
            logger.info(f"Starting SEBEK speech simulator with {args.sim_file}")
            return sim_recognize_file(
                wav_file=args.sim_file,
                model_path=args.model,
                sebek_url=args.sebek_url,
                persist_dir=args.persist_dir,
            )

        if not HAS_AUDIO:
            logger.error("sounddevice not available. Install with: pip install sounddevice")
            return 1

        # Initialize TTS
        tts = TextToSpeech(enable=not args.no_tts)

        # Create multiprocessing components
        audio_queue: Queue = Queue()
        stop_event: Event = Event()

        # Start worker processes
        recorder = Process(
            target=recorder_worker,
            args=(audio_queue, stop_event, args.device),
            daemon=True,
        )
        recognizer = Process(
            target=recognizer_worker,
            args=(audio_queue, stop_event, args.model, args.sebek_url, args.persist_dir),
            daemon=True,
        )

        logger.info("Starting SEBEK speech agent")
        recorder.start()
        recognizer.start()

        # Initial greeting
        if tts.is_available():
            tts.speak("SEBEK speech agent online")

        # Monitor worker processes
        try:
            while True:
                time.sleep(1)
                if not recorder.is_alive() or not recognizer.is_alive():
                    logger.warning("Worker process died; shutting down")
                    break
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")

        # Cleanup
        stop_event.set()
        time.sleep(0.5)
        for proc in [recorder, recognizer]:
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=2)
                if proc.is_alive():
                    proc.kill()

        logger.info("SEBEK speech agent stopped")
        return 0

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
