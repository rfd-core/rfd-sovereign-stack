# SEBEK Troubleshooting Guide

## Connection Issues

### Ollama Not Found

**Error:** `Could not connect to SEBEK engine at http://localhost:11434`

**Solutions:**

1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Check Ollama installation:
   ```bash
   ollama --version
   ollama serve  # Start Ollama
   ```

3. Override URL if Ollama is on different host:
   ```bash
   export SEBEK_OLLAMA_URL=http://remote-host:11434
   make run-dashboard
   ```

### Port Already in Use

**Error:** `Address already in use` when starting dashboard

**Solutions:**

```bash
# Find what's using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or use different port
streamlit run -m sebek.dashboard --server.port 8502
```

## Installation Issues

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'sebek'`

**Solutions:**

```bash
# Reinstall in development mode
pip install -e .

# Or with all dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import sebek; print(sebek.__version__)"
```

### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solutions:**

```bash
# Reinstall all dependencies
pip install --upgrade -e ".[dev]"

# Or install specific components
pip install streamlit langchain chromadb vosk pyttsx3
```

### Python Version Issues

**Error:** `Python 3.9 not supported` or version-related errors

**Solutions:**

```bash
# Check Python version
python --version  # Should be 3.10+

# On Windows/macOS, try:
python3 --version
python3 -m venv venv

# On Linux:
python3.11 -m venv venv
```

## Speech Recognition Issues

### Vosk Model Not Found

**Error:** `Vosk model not found at: ./models/vosk-model-small-en-us-0.15`

**Solutions:**

```bash
# Download model
make setup-speech

# Or manually
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip -o vosk-model-small-en-us-0.15.zip

# Or specify custom model path
export SEBEK_VOSK_MODEL=/path/to/your/model
make run-speech
```

### No Microphone Input

**Error:** Speech agent starts but doesn't recognize audio

**Solutions:**

```bash
# List audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Use specific device
python -m sebek.speech.agent --device 0  # Try 0, 1, 2, etc.

# Check microphone permissions (Linux)
groups $(whoami)  # Should include 'audio' group
sudo usermod -a -G audio $USER
```

### TTS Not Working

**Error:** No audio feedback from text-to-speech

**Solutions:**

```bash
# Check pyttsx3 installation
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"

# Disable TTS if not needed
python -m sebek.speech.agent --no-tts

# Install audio backend (Linux)
sudo apt install -y espeak libespeak1
```

## Vector Database Issues

### Chroma Connection Failed

**Error:** `VectorDBError: Failed to initialize vector database`

**Solutions:**

```bash
# Verify LangChain is installed
pip install langchain-community chromadb

# Check database directory permissions
ls -la sebek_memory_db/

# Remove corrupted database and reingest
rm -rf sebek_memory_db/
make run-ingest
```

### Ingestion Fails

**Error:** `IngestionError: No documents found in vault`

**Solutions:**

```bash
# Check vault path exists
ls -la $SEBEK_VAULT_PATH

# Or override:
export SEBEK_VAULT_PATH=/path/to/documents
make run-ingest

# Check file extensions (should be .md, .txt, .csv)
find $SEBEK_VAULT_PATH -type f -name "*.*" | head
```

### Embedding Timeout

**Error:** `requests.exceptions.Timeout: HTTPConnectionPool timeout`

**Solutions:**

```bash
# Check Ollama is responsive
curl -m 30 http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama

# Increase timeout (edit sebek/config.py)
SEBEK_LLM_MAX_TOKENS=1024  # Reduce if too large
```

## Test & Development Issues

### Tests Failing

**Error:** `pytest tests/ fails with assertion errors`

**Solutions:**

```bash
# Run specific test with verbose output
pytest tests/test_config.py -vv

# Run with print statements
pytest tests/ -s

# Run with pdb debugger
pytest tests/ --pdb
```

### Linting Errors

**Error:** `Black/isort/flake8 fails on commit`

**Solutions:**

```bash
# Auto-format code
make format

# Re-stage formatted files
git add .
git commit -m "message"

# Or bypass pre-commit (not recommended)
git commit --no-verify
```

## Performance Issues

### Dashboard Slow

**Solutions:**

```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/

# Reduce Chroma search results
export SEBEK_SIMILARITY_K=1  # Default is 3

# Reduce chunk size for faster embeddings
export SEBEK_CHUNK_SIZE=250  # Default is 500
```

### High Memory Usage

**Solutions:**

```bash
# Check memory usage
ps aux | grep sebek

# Reduce Ollama context
export OLLAMA_NUM_GPU=0  # Disable GPU acceleration

# Restart services
sudo systemctl restart sebek-dashboard
sudo systemctl restart ollama
```

### Slow Ingestion

**Solutions:**

```bash
# Increase batch size for faster ingestion
make run-ingest -- --batch-size 10000

# Check disk I/O
iostat -xz 1

# Use SSD if available (much faster than HDD)
```

## Logging & Debugging

### Enable Debug Logging

```bash
# Set log level
export SEBEK_LOG_LEVEL=DEBUG
make run-dashboard

# View logs
tail -f logs/sebek.log
```

### Capture Full Stack Trace

```bash
# Run with Python debugger
python -m pdb -m sebek.dashboard

# Or catch exception output
python -m sebek.dashboard 2>&1 | tee debug.log
```

## Getting Help

1. **Check logs:**
   ```bash
   journalctl -u sebek-dashboard -f  # Systemd logs
   tail -f logs/sebek.log             # Application logs
   ```

2. **Search GitHub issues:**
   https://github.com/rfd-core/rfd-sovereign-stack/issues

3. **Create an issue with:**
   - Error message (full stack trace)
   - Steps to reproduce
   - Python version (`python --version`)
   - OS/platform
   - Configuration (SEBEK_* env vars)

4. **Join discussions:**
   https://github.com/rfd-core/rfd-sovereign-stack/discussions
