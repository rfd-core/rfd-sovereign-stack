#!/usr/bin/env python3
"""Legacy compatibility wrapper for SEBEK ingestion CLI.

This script is deprecated. Use:
    python -m sebek.ingestion_cli
"""

from __future__ import annotations

import sys
import warnings

from sebek.ingestion_cli import main


if __name__ == "__main__":
    warnings.warn(
        "sebek_mass_digest.py is deprecated; use 'python -m sebek.ingestion_cli'.",
        DeprecationWarning,
        stacklevel=1,
    )
    sys.exit(main())
