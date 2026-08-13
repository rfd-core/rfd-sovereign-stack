#!/usr/bin/env python3
"""
sebek_speech_agent.py

Multiprocess speech agent for SEBEK using Vosk (offline ASR) and pyttsx3 (TTS).
- Captures microphone audio with sounddevice
- Runs Vosk recognizer in a worker and posts final transcripts to SEBEK at /api/observe
- Simulator mode to replay a WAV file for testing
- Persist audio snippets and produce minimal logs

Usage examples:
  python3 sebek_speech_agent.py --model /opt/vosk-model-small-en-us-0.15 --persist-dir /var/lib/sebek/speech
  python3 sebek_speech_agent.py --sim-file examples/test.wav --model /opt/vosk-model-small-en-us-0.15

Systemd unit provided in repo: sebek-speech.service

"""

import argparse
import json
import os
import queue
import sys
import time
import uuid
import logging
from pathlib import Path
from multiprocessing import Process, Queue, Event

import requests

# sounddevice and vosk are optional at import time for simulator mode tests
try:
    import sounddevice as sd
    import numpy as np
    HAVE_AUDIO = True
except Exception:
    HAVE_AUDIO = False

try:
    from vosk import Model, KaldiRecognizer
    HAVE_VOSK = True
except Exception:
    HAVE_VOSK = False

try:
    import pyttsx3
    HAVE_TTS = True
except Exception:
    HAVE_TTS = False

import wave

DEFAULT_SEBEK_URL = "http://localhost:11434/api/observe"
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 8000  # bytes (int16)


def init_logging(log_path: Path = None):
    log = logging.getLogger("sebek_speech_agent")
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    log.addHandler(sh)
    if log_path:
        fh = logging.FileHandler(log_path)
        fh.setFormatter(fmt)
        log.addHandler(fh)
    return log


def post_to_sebek(url, payload, max_retries=3, backoff=1.0, logger=None):
    headers = {"Content-Type": "application/json"}
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=5)
            if logger:
                logger.info(f"Posted to SEBEK: {payload.get('type')} -> status {r.status_code}")
            return r
        except Exception as e:
            if logger:
                logger.warning(f"Failed to post to SEBEK (attempt {attempt}): {e}")
            time.sleep(backoff * attempt)
    return None


def save_wav_from_bytes(path: Path, audio_bytes: bytes, samplerate=SAMPLE_RATE, channels=CHANNELS):
    # audio_bytes is raw int16 bytes
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(samplerate)
        wf.writeframes(audio_bytes)


def recorder_worker(audio_q: Queue, stop_evt: Event, device=None, samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE, logger=None):
    if not HAVE_AUDIO:
        raise RuntimeError("sounddevice is not available on this system")

    def callback(indata, frames, time_info, status):
        if status:
            if logger:
                logger.warning(f"InputStream status: {status}")
        # indata is a numpy array of shape (frames, channels)
        audio_q.put(indata.copy())

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=int(blocksize/2), dtype='int16', channels=CHANNELS, device=device, callback=callback):
            if logger:
                logger.info("Recorder started, capturing microphone audio...")
            while not stop_evt.is_set():
                time.sleep(0.1)
    except Exception as e:
        if logger:
            logger.exception(f"Recorder encountered an error: {e}")
        stop_evt.set()


def recognizer_worker(audio_q: Queue, stop_evt: Event, model_path: str, sebek_url: str, persist_dir: Path, logger=None):
    if not HAVE_VOSK:
        raise RuntimeError("vosk is not installed or failed to import")

    if not os.path.exists(model_path):
        raise RuntimeError(f"Vosk model not found at {model_path}")

    model = Model(model_path)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    buffer_chunks = []
    bytes_buffer = bytearray()

    while not stop_evt.is_set():
        try:
            chunk = audio_q.get(timeout=1.0)
        except queue.Empty:
            continue

        # chunk is numpy array int16 -> convert to bytes
        if isinstance(chunk, bytes):
            raw = chunk
        else:
            raw = chunk.tobytes()

        bytes_buffer.extend(raw)

        if rec.AcceptWaveform(raw):
            result_json = json.loads(rec.Result())
            text = result_json.get("text", "").strip()
            if text:
                # persist audio snippet
                ts = time.strftime("%Y%m%d_%H%M%S")
                fname = f"speech_{ts}_{uuid.uuid4().hex[:8]}.wav"
                persist_dir.mkdir(parents=True, exist_ok=True)
                wav_path = persist_dir / fname
                try:
                    save_wav_from_bytes(wav_path, bytes(bytes_buffer))
                except Exception as e:
                    if logger:
                        logger.warning(f"Failed to save wav: {e}")

                payload = {
                    "type": "speech",
                    "source": "mic",
                    "text": text,
                    "metadata": {
                        "audio_path": str(wav_path),
                        "timestamp": ts
                    }
                }
                post_to_sebek(sebek_url, payload, logger=logger)

            # reset buffer
            bytes_buffer = bytearray()
        else:
            # partial result available (optional)
            # partial = json.loads(rec.PartialResult()).get("partial","")
            # handle partials if desired
            pass

    if logger:
        logger.info("Recognizer worker stopping")


def sim_recognize_file(wav_file: Path, model_path: str, sebek_url: str, persist_dir: Path, logger=None):
    # read wav, feed to Vosk in chunks to simulate real-time
    if not HAVE_VOSK:
        raise RuntimeError("vosk is not installed or failed to import")
    if not wav_file.exists():
        raise RuntimeError(f"Sim file not found: {wav_file}")

    wf = wave.open(str(wav_file), "rb")
    if wf.getnchannels() != CHANNELS or wf.getframerate() != SAMPLE_RATE:
        if logger:
            logger.warning("Sim file sampling params differ from expected — results may vary")

    model = Model(model_path)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    bytes_buffer = bytearray()
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text = res.get("text", "").strip()
            if text:
                ts = time.strftime("%Y%m%d_%H%M%S")
                fname = f"sim_speech_{ts}_{uuid.uuid4().hex[:8]}.wav"
                persist_dir.mkdir(parents=True, exist_ok=True)
                wav_path = persist_dir / fname
                try:
                    # optionally persist the whole sim file once per result
                    save_wav_from_bytes(wav_path, data)
                except Exception:
                    pass
                payload = {"type": "speech", "source": "sim", "text": text, "metadata": {"audio_path": str(wav_path), "timestamp": ts}}
                post_to_sebek(sebek_url, payload, logger=logger)
        else:
            pass
        time.sleep(0.05)

    # final
    final = json.loads(rec.FinalResult())
    if final.get("text", "").strip():
        payload = {"type": "speech", "source": "sim", "text": final.get("text",""), "metadata": {"audio_path": str(wav_file), "timestamp": time.strftime("%Y%m%d_%H%M%S")}}
        post_to_sebek(sebek_url, payload, logger=logger)

    if logger:
        logger.info("Sim recognition complete")


def tts_say(text: str):
    if not HAVE_TTS:
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def main():
    p = argparse.ArgumentParser(description="SEBEK Speech Agent (Vosk)")
    p.add_argument("--model", type=str, default="./models/vosk-model-small-en-us-0.15", help="Path to Vosk model directory")
    p.add_argument("--sebek-url", type=str, default=DEFAULT_SEBEK_URL, help="SEBEK ingest URL")
    p.add_argument("--persist-dir", type=str, default="./sebek_speech_data", help="Directory to persist audio snippets")
    p.add_argument("--log", type=str, default="./sebek_speech.log", help="Log file path")
    p.add_argument("--device", type=int, default=None, help="Input device index for sounddevice")
    p.add_argument("--sim-file", type=str, default=None, help="Simulator WAV file (if provided, will run file instead of live mic)")
    p.add_argument("--no-tts", action="store_true", help="Disable local TTS feedback")
    args = p.parse_args()

    logger = init_logging(Path(args.log))

    model_path = args.model
    sebek_url = args.sebek_url
    persist_dir = Path(args.persist_dir)

    # Basic check
    if args.sim_file:
        if not HAVE_VOSK:
            logger.error("Vosk is required for simulator mode. Install vosk package and a model.")
            sys.exit(1)
        sim_file = Path(args.sim_file)
        logger.info(f"Starting SIM mode using {sim_file}")
        try:
            sim_recognize_file(sim_file, model_path, sebek_url, persist_dir, logger=logger)
            logger.info("SIM finished; exiting")
        except Exception as e:
            logger.exception(e)
        sys.exit(0)

    # Live mode
    if not HAVE_AUDIO:
        logger.error("sounddevice is not available. Install sounddevice and ensure audio devices are accessible.")
        sys.exit(1)
    if not HAVE_VOSK:
        logger.error("vosk not available. Install vosk package and place model at --model")
        sys.exit(1)

    audio_q = Queue()
    stop_evt = Event()

    recorder = Process(target=recorder_worker, args=(audio_q, stop_evt, args.device, SAMPLE_RATE, BLOCKSIZE, logger), daemon=True)
    recognizer = Process(target=recognizer_worker, args=(audio_q, stop_evt, model_path, sebek_url, persist_dir, logger), daemon=True)

    try:
        logger.info("Starting recorder and recognizer processes")
        recorder.start()
        recognizer.start()

        # initial TTS greeting
        if not args.no_tts and HAVE_TTS:
            tts_say("SEBEK speech agent online")

        while True:
            time.sleep(1)
            if not recorder.is_alive() or not recognizer.is_alive():
                logger.warning("One of the worker processes died; stopping agent")
                break
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received; shutting down")
    finally:
        stop_evt.set()
        time.sleep(0.5)
        if recorder.is_alive():
            recorder.terminate()
        if recognizer.is_alive():
            recognizer.terminate()
        logger.info("SEBEK speech agent stopped")


if __name__ == "__main__":
    main()
