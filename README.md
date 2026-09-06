# rfd-sovereign-stack

A sovereign, portable, and cost-effective e-commerce platform for the Red Feather Dynasty, built on a Vultr-ready headless architecture. · Built with Manus.

## Current Architecture & Files
- **Language:** Python
- **Core Components:**
  - `sebek/dashboard.py`: Streamlit dashboard (`streamlit run -m sebek.dashboard`).
  - `sebek/ingestion_cli.py`: Ingestion CLI (`python -m sebek.ingestion_cli`).
  - `sebek/speech/agent.py`: Speech agent (`python -m sebek.speech.agent`).
  - `Modelfile`: DSOS Infrastructure Baseline configuration.
  - `operations_ledger.txt` & `sebek_audit.txt`: Infrastructure logs and audits.

Legacy wrappers (`sebek_dash.py`, `sebek_mass_digest.py`, `sebek_speech_agent.py`) are deprecated compatibility entrypoints.
