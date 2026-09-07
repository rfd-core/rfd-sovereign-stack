#!/usr/bin/env python3
"""Legacy compatibility wrapper for SEBEK speech agent.

This script is deprecated. Use:
    python -m sebek.speech.agent
"""

from __future__ import annotations

import sys
import warnings

from sebek.speech.agent import main


if __name__ == "__main__":
    warnings.warn(
        "sebek_speech_agent.py is deprecated; use 'python -m sebek.speech.agent'.",
        DeprecationWarning,
        stacklevel=1,
    )
    sys.exit(main())
