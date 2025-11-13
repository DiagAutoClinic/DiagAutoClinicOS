"""Compatibility shim: historical plural module name

Some tests import `calibrations_resets` (plural). The real implementation
is `calibrations_reset.py` (singular). Re-export the public symbols so tests
continue to work without editing test files.
"""
from calibrations_reset import (
    CalibrationProcedure,
    CalibrationsResetsManager,
    ResetType,
    calibrations_resets_manager,
)

__all__ = [
    "CalibrationProcedure",
    "CalibrationsResetsManager",
    "ResetType",
    "calibrations_resets_manager",
]
