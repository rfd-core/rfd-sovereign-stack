#!/usr/bin/env python3
"""Legacy compatibility wrapper for SEBEK dashboard.

This script is deprecated. Use:
    streamlit run /path/to/repo/sebek/dashboard.py
or:
    streamlit run -m sebek.dashboard
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import warnings


def main() -> int:
    """Launch the package dashboard module via Streamlit."""
    warnings.warn(
        "sebek_dash.py is deprecated; use 'streamlit run -m sebek.dashboard'.",
        DeprecationWarning,
        stacklevel=2,
    )
    spec = importlib.util.find_spec("sebek.dashboard")
    if spec is None or spec.origin is None:
        print("Unable to locate sebek.dashboard module.")
        return 1

    cmd = [sys.executable, "-m", "streamlit", "run", spec.origin, *sys.argv[1:]]
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
