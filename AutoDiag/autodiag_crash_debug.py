"""
AutoDiag crash-debug bootstrap.
Provides a lightweight, always-safe crash detection hook used by main.py.
"""

from __future__ import annotations

import faulthandler
import logging
import os
import sys


def install_crash_detection(log_file: str | None = None) -> bool:
    """Install basic crash diagnostics and return True when enabled.

    This is intentionally defensive: if anything fails, we return False
    and avoid crashing application startup.
    """
    try:
        target = log_file or os.path.join(os.path.dirname(__file__), "autodiag_crash_debug.log")
        # Append in binary mode for faulthandler compatibility.
        fh = open(target, "ab")
        faulthandler.enable(file=fh, all_threads=True)
        logging.getLogger(__name__).info("Crash detection enabled: %s", target)
        return True
    except Exception as exc:  # pragma: no cover - best effort only
        try:
            print(f"Crash detection setup failed: {exc}", file=sys.stderr)
        except Exception:
            pass
        return False
