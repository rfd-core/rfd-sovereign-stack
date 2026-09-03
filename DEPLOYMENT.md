# SEBEK Deployment Guide

## Local Machine

### Prerequisites
- Python 3.10+
- Ollama installed and running
- Git

### Installation

```bash
git clone https://github.com/rfd-core/rfd-sovereign-stack.git
cd rfd-sovereign-stack
make dev-setup
make run-dashboard
```

## WSL (Windows Subsystem for Linux)

### Setup WSL2

```bash
# In PowerShell (Admin)
wsl --install -d Ubuntu-22.04
```

### Install Dependencies

```bash
# In WSL terminal
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Clone and setup
git clone https://github.com/rfd-core/rfd-sovereign-stack.git
cd rfd-sovereign-stack
make dev-setup
```

### Configure Vault Path

```bash
# .env in WSL
SEBEK_VAULT_PATH=/mnt/c/Users/YourUsername/Documents/vault
```

### Running Services

```bash
# Terminal 1: Ollama (runs on Windows, accessible from WSL)
curl http://localhost:11434/api/tags

# Terminal 2: SEBEK Dashboard
make run-dashboard
# Access at http://localhost:8501

# Terminal 3: Speech Agent
make setup-speech
make run-speech
```

## Docker

### Build Image

```bash
docker build -t sebek:latest .
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_MODELS=/root/.ollama/models

  sebek:
    build: .
    ports:
      - "8501:8501"
    environment:
      - SEBEK_OLLAMA_URL=http://ollama:11434
      - SEBEK_DB_DIR=/app/data/vectordb
      - SEBEK_VAULT_PATH=/app/data/vault
    volumes:
      - ./data:/app/data
    depends_on:
      - ollama
    command: streamlit run -m sebek.dashboard --server.address 0.0.0.0

volumes:
  ollama_data:
```

```bash
docker-compose up -d
```

## Vultr VPS

### 1. Create Vultr Instance

- OS: Ubuntu 22.04 LTS
- Plan: 2GB+ RAM (4GB recommended)
- Location: Your choice

### 2. Initial Setup

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.11 python3.11-venv python3-pip git curl

# Create non-root user
useradd -m -s /bin/bash sebek
su - sebek
```

### 3. Install Ollama

```bash
curl https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull a model
ollama pull nomic-embed-text
ollama pull sebek-core  # or another model
```

### 4. Install SEBEK

```bash
cd ~
git clone https://github.com/rfd-core/rfd-sovereign-stack.git
cd rfd-sovereign-stack

make dev-setup
make setup-speech  # Download Vosk model
```

### 5. Systemd Service

```ini
# /etc/systemd/system/sebek-dashboard.service
[Unit]
Description=SEBEK Dashboard
After=network.target ollama.service

[Service]
Type=simple
User=sebek
WorkingDirectory=/home/sebek/rfd-sovereign-stack
Environment="PATH=/home/sebek/rfd-sovereign-stack/venv/bin"
Environment="SEBEK_OLLAMA_URL=http://localhost:11434"
Environment="SEBEK_LOG_LEVEL=INFO"
ExecStart=/home/sebek/rfd-sovereign-stack/venv/bin/streamlit run -m sebek.dashboard --server.address 0.0.0.0 --server.port 8501
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable sebek-dashboard
sudo systemctl start sebek-dashboard
sudo systemctl status sebek-dashboard
```

```ini
# /etc/systemd/system/sebek-speech.service
[Unit]
Description=SEBEK Speech Agent
After=network.target ollama.service

[Service]
Type=simple
User=sebek
WorkingDirectory=/home/sebek/rfd-sovereign-stack
Environment="PATH=/home/sebek/rfd-sovereign-stack/venv/bin"
Environment="SEBEK_OLLAMA_URL=http://localhost:11434"
ExecStart=/home/sebek/rfd-sovereign-stack/venv/bin/python -m sebek.speech.agent --model /home/sebek/rfd-sovereign-stack/models/vosk-model-small-en-us-0.15
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6. Nginx Reverse Proxy (Optional)

```nginx
# /etc/nginx/sites-available/sebek
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/sebek /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL with Let's Encrypt (Optional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Check Services

```bash
# Dashboard status
sudo systemctl status sebek-dashboard

# Speech agent status
sudo systemctl status sebek-speech

# Ollama status
sudo systemctl status ollama

# View logs
journalctl -u sebek-dashboard -f
journalctl -u sebek-speech -f
```

### Resource Usage

```bash
# Monitor processes
top  # Press q to exit

# Disk usage
df -h

# Memory usage
free -h
```

## Troubleshooting

### Ollama Not Starting

```bash
# Check status
sudo systemctl status ollama

# View logs
journalctl -u ollama -n 50

# Restart
sudo systemctl restart ollama
```

### Dashboard Not Accessible

```bash
# Check if running
sudo systemctl status sebek-dashboard

# View logs
journalctl -u sebek-dashboard -f

# Test port
curl http://localhost:8501
```

### High Memory Usage

```bash
# Reduce Ollama context window
OLLAMA_NUM_GPU=0  # Disable GPU if available but causing issues

# Reduce model loaded
ollama list  # See loaded models
```

## Backup & Recovery

```bash
# Backup vector database
tar -czf sebek_backup.tar.gz sebek_memory_db/

# Backup vault (if storing locally)
tar -czf vault_backup.tar.gz /path/to/vault/

# Restore
tar -xzf sebek_backup.tar.gz
```
