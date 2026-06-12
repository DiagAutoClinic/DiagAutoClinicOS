#!/usr/bin/env python3
"""
CAN Bus REF File Parser  —  DACOS DBC-Backend

⚠  REPLACED with DBC-based CAN database.
This module is retained for backward compatibility only.
All queries delegate to shared.can_database (the DACOS DBC engine).

No heuristic guessing.  No mock data.  Truth only.
"""

import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

from shared.can_database import (
    get_database,
    VehicleCANDatabase,
    CANMessage as DBCMessage,
    CANSignal as DBCSignal,
)

logger = logging.getLogger(__name__)

# Re-export canonical data classes (same shapes as before)
CANSignal    = DBCSignal
CANMessage   = DBCMessage
VehicleCANDatabase = VehicleCANDatabase


class REFFileParser:
    """
    Backward-compatible REF file parser — now DBC-backed.

    Instead of reading .REF binary files it loads signal definitions
    from the DACOS CAN_DBC/ database.
    """

    HEADER_SIGNATURE = b"Racelogic Can Data File V1a"

    def __init__(self, ref_dir: Optional[Path] = None):
        # ref_dir is ignored — all data comes from CAN_DBC/
        self._ref_dir = ref_dir
        self._cache: Dict[str, VehicleCANDatabase] = {}
        self._dbc = get_database()

    # ── listing ──────────────────────────────────────────────────────

    def list_available_vehicles(self) -> List[Tuple[str, str, str]]:
        """
        Return (manufacturer, model, filename) tuples.
        The filename is an identifier that can be passed to parse_file().
        """
        result = []
        for mfr in self._dbc.manufacturers():
            for model in self._dbc.models_for(mfr):
                # Build a filename key
                fname = f"{mfr}-{model}.dbc" if model else f"{mfr}.dbc"
                result.append((mfr, model, fname))
        return sorted(result)

    def get_manufacturers(self) -> List[str]:
        return self._dbc.manufacturers()

    def get_models_for_manufacturer(self, manufacturer: str) -> List[str]:
        return self._dbc.models_for(manufacturer)

    # ── parsing ──────────────────────────────────────────────────────

    def parse_file(self, filename: str) -> Optional[VehicleCANDatabase]:
        """Return a VehicleCANDatabase from DBC data matching the filename."""
        # Check cache
        if filename in self._cache:
            return self._cache[filename]

        # Map filename to manufacturer/model
        stem = Path(filename).stem
        mfr, model = _split_fname(stem)

        vdb = self._dbc.vehicle(mfr, model)
        if vdb is None:
            logger.warning("No DBC vehicle for '%s' (mfr=%s, model=%s)", filename, mfr, model)
            return None

        self._cache[filename] = vdb
        logger.info(
            "DBC-backed: %s — %d messages, %d signals",
            filename, len(vdb.messages),
            sum(len(m.signals) for m in vdb.messages.values()),
        )
        return vdb


def _split_fname(stem: str) -> Tuple[str, str]:
    """Split a filename stem into (manufacturer, model)."""
    multi = {
        "Alfa Romeo", "Aston Martin", "Chevrolet", "Citroen",
        "Land Rover", "Mercedes", "Rolls Royce", "Range Rover",
        "Vauxhall", "Volkswagen",
    }
    for m in multi:
        if stem.startswith(m + "-"):
            return m, stem[len(m) + 1:]
    if "-" in stem:
        parts = stem.split("-", 1)
        return parts[0].strip(), parts[1].strip()
    return stem, ""


# ── global instance & convenience functions ────────────────────────────

ref_parser = REFFileParser()


def get_vehicle_database(manufacturer: str, model: str = "") -> Optional[VehicleCANDatabase]:
    """Get CAN database for a specific vehicle (DBC-backed)."""
    return ref_parser._dbc.vehicle(manufacturer, model)


def list_all_vehicles() -> List[Tuple[str, str, str]]:
    """List all available vehicles."""
    return ref_parser.list_available_vehicles()


def get_all_manufacturers() -> List[str]:
    """Get all available manufacturers."""
    return ref_parser.get_manufacturers()
