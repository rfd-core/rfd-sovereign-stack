SEBEK Speech Agent (Vosk) - README

This directory adds a multiprocess speech agent that captures microphone audio, runs offline ASR with Vosk, and posts final transcripts to SEBEK at http://localhost:11434/api/observe

Quick install (Linux, sudo required):

1) Install system packages (Debian/Ubuntu example):
   sudo apt update
   sudo apt install -y python3-venv python3-pip build-essential libsndfile1 ffmpeg

2) Create a Python virtualenv and install requirements:
   python3 -m venv /opt/sebek-speech-venv
   source /opt/sebek-speech-venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements-speech.txt

3) Download a Vosk model (small English recommended for quick testing):
   sudo mkdir -p /opt/vosk-models
   cd /opt/vosk-models
   # Example model (adjust version if needed):
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   sudo mv vosk-model-small-en-us-0.15 /opt/vosk-model-small-en-us-0.15

4) Copy repository to /opt and install systemd unit:
   sudo cp -r . /opt/rfd-sovereign-stack
   sudo cp sebek-speech.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable sebek-speech
   sudo systemctl start sebek-speech

5) Test without systemd (from the virtualenv):
   python sebek_speech_agent.py --model /opt/vosk-model-small-en-us-0.15 --persist-dir /var/lib/sebek/speech

Simulator mode (replay a WAV file):
   python sebek_speech_agent.py --sim-file examples/test.wav --model /opt/vosk-model-small-en-us-0.15

Notes & Troubleshooting:
- Ensure microphone permissions and pulse/ALSA config are correct when running under systemd; running as root may not have access to user devices. If you prefer, create a dedicated user (sebek) and add to audio group, and update the unit file's User/Group.
- SEBEK endpoint: the agent posts JSON payloads to /api/observe. Adjust --sebek-url if your SEBEK engine listens on a different path/port.
- For better accuracy, use a larger Vosk model or whisper.cpp/Whisper models if you have resources.

