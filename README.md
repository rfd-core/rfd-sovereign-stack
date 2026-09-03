# SEBEK: Sovereign Local Intelligence Engine

🦅 **A unified digital operating environment (DSOS)** combining:
- **Headless e-commerce platform** – Cost-effective, sovereign, portable
- **Local LLM inference** – Ollama-powered, no cloud dependency
- **Voice-driven control** – Offline ASR (Vosk) + TTS (pyttsx3)
- **Semantic knowledge retrieval** – RAG with LangChain + Chroma

**Built for the Red Feather Dynasty.** Designed to run anywhere: local machines, WSL, Vultr VPS, or bare metal.

---

## ✨ Features

### 🎤 Voice-First Interface
- Offline speech recognition (Vosk model) – no internet required
- Real-time audio capture and processing
- Text-to-speech feedback (pyttsx3)
- Multiprocess design for responsive UI

### 🧠 Intelligent Context
- Semantic document retrieval (RAG)
- Persistent vector database (Chroma)
- Batch document ingestion from file vaults
- Context-aware LLM responses

### 🎛️ Unified Control Center
- Streamlit web dashboard
- Real-time chat with LLM
- System health monitoring
- Direct command interface to SEBEK core

### 🔒 Sovereign & Portable
- No external API dependencies (uses local Ollama)
- Environment-based configuration
- Cross-platform (Linux, WSL, macOS, Vultr)
- Docker-ready architecture

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- Vosk model (auto-downloaded via `make setup-speech`)

### Installation

```bash
# Clone repository
git clone https://github.com/rfd-core/rfd-sovereign-stack.git
cd rfd-sovereign-stack

# Setup development environment
make dev-setup

# Verify installation
make check
```

### Running SEBEK

#### 1. Dashboard (Web UI)
```bash
make run-dashboard
# Opens at http://localhost:8501
```

#### 2. Document Ingestion
```bash
make run-ingest
# Loads documents from vault into vector database
```

#### 3. Speech Agent (Microphone Listener)
```bash
make setup-speech  # Download Vosk model (one-time)
make run-speech
# Listens for voice commands
```

---

## 📋 Architecture

### Package Structure

```
sebek/
├── __init__.py           # Package initialization
├── config.py             # Centralized configuration
├── dashboard.py          # Streamlit UI
├── ingestion.py          # Document ingestion pipeline
├── ingestion_cli.py      # Ingestion CLI entry point
│
├── utils/
│   ├── __init__.py
│   ├── logging.py        # Logging infrastructure
│   ├── errors.py         # Custom exceptions
│   └── vectordb.py       # Vector DB utilities
│
└── speech/
    ├── __init__.py
    ├── recognizer.py     # Vosk/TTS wrappers
    └── agent.py          # Multiprocess speech agent
```

### Data Flow

```
🎤 Microphone
  ↓
[Speech Agent] → Vosk ASR → Text → POST to /api/observe
  ↓
[Ingestion Pipeline] → TextLoader → TextSplitter → Chroma
  ↓
[LLM Query] → Ollama + RAG Context → Streamlit Dashboard
  ↓
💬 Chat Response
```

---

## 🔧 Configuration

SEBEK uses environment variables for configuration. Create a `.env` file:

```bash
# .env
SEBEK_OLLAMA_URL=http://localhost:11434
SEBEK_EMBEDDING_MODEL=nomic-embed-text
SEBEK_CHAT_MODEL=sebek-core
SEBEK_DB_DIR=./sebek_memory_db
SEBEK_VAULT_PATH=/path/to/vault
SEBEK_VOSK_MODEL=./models/vosk-model-small-en-us-0.15
SEBEK_LOG_LEVEL=INFO
```

See [`sebek/config.py`](sebek/config.py) for complete configuration options.

---

## 📚 Development

### Running Tests

```bash
make test              # All tests with coverage
make test-unit         # Unit tests only
make test-fast         # Without coverage (faster)
```

### Code Quality

```bash
make lint              # Check code style
make format            # Auto-format code (black + isort)
make check             # Full quality check (lint + test)
```

### Common Tasks

```bash
make install           # Install package
make clean             # Remove build artifacts
make help              # Show all available commands
```

For detailed development setup, see [DEV_SETUP.md](DEV_SETUP.md).

---

## 📖 Documentation

- [**DEV_SETUP.md**](DEV_SETUP.md) – Development environment setup
- [**CONTRIBUTING.md**](CONTRIBUTING.md) – Contribution guidelines
- [**sebek/config.py**](sebek/config.py) – Configuration reference
- [**tests/**](tests/) – Example tests and fixtures

---

## 🔄 Deployment

### Local Development

```bash
# Standard setup
make dev-setup
make run-dashboard
```

### WSL (Windows Subsystem for Linux)

```bash
# Install Python 3.10+
sudo apt update && sudo apt install python3.10 python3.10-venv python3-pip

# Follow standard setup
git clone ...
cd rfd-sovereign-stack
make dev-setup
```

### Docker

```dockerfile
# Example Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["streamlit", "run", "-m", "sebek.dashboard"]
```

```bash
docker build -t sebek:latest .
docker run -p 8501:8501 sebek:latest
```

### Vultr VPS

See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment instructions.

---

## 🐛 Troubleshooting

### Ollama Not Accessible

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Override URL if needed
SEBEK_OLLAMA_URL=http://remote-machine:11434 make run-dashboard
```

### Missing Dependencies

```bash
# Reinstall with all dependencies
pip install -e ".[dev]"
```

### Speech Recognition Not Working

```bash
# Download Vosk model
make setup-speech

# Verify model exists
ls models/vosk-model-small-en-us-0.15/
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

---

## 📋 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Core Infrastructure | ✅ Complete | Config, logging, errors |
| Vector DB Integration | ✅ Complete | Chroma with context-length handling |
| Document Ingestion | ✅ Complete | Batch loading + chunking |
| Streamlit Dashboard | ✅ Complete | Chat + vault explorer |
| Speech Recognition | ✅ Complete | Vosk + TTS + multiprocess |
| Test Suite | ✅ Complete | 50%+ coverage with fixtures |
| CI/CD Workflows | ✅ Complete | GitHub Actions for lint/test/build |
| Documentation | ✅ Complete | Setup guide + dev guide + API docs |

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick start:**
```bash
make dev-setup        # Setup environment
git checkout -b feature/my-feature  # Create branch
# Make changes...
make check            # Run lint + tests
git push origin feature/my-feature
# Create Pull Request on GitHub
```

---

## 📝 License

MIT License – See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

**Built with:**
- [Streamlit](https://streamlit.io/) – Web UI framework
- [LangChain](https://langchain.com/) – LLM orchestration
- [Ollama](https://ollama.ai/) – Local LLM inference
- [Vosk](https://alphacephei.com/vosk/) – Offline ASR
- [Chroma](https://www.trychroma.com/) – Vector database

**For:** The Red Feather Dynasty 🦅

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/rfd-core/rfd-sovereign-stack/issues)
- **Discussions:** [GitHub Discussions](https://github.com/rfd-core/rfd-sovereign-stack/discussions)
- **Docs:** [DEV_SETUP.md](DEV_SETUP.md) | [CONTRIBUTING.md](CONTRIBUTING.md)

---

**SEBEK v0.1.0** | Sovereign • Local • Intelligent • Free
