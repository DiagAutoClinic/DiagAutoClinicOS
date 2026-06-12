#!/usr/bin/env python3
"""
Racelogic .REF File Parser  —  DACOS DBC-Backend

⚠  REPLACED with DBC-based CAN database.
This module is retained for API compatibility only.
All queries delegate to shared.can_database (the DACOS DBC engine).

No heuristic guessing.  No mock data.  Truth only.
"""

import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from shared.can_database import (
    CANDatabase,
    get_database,
    get_vehicle_database,
    VehicleCANDatabase as DACOSVehicleDB,
)

logger = logging.getLogger(__name__)


# ── backward‑compat data classes ───────────────────────────────────────

@dataclass
class RacelogicParameter:
    """Backward‑compatible parameter type (now DBC‑backed)."""
    name: str
    can_id: int
    channel: int = 0
    conversion_factor: float = 1.0
    conversion_offset: float = 0.0
    unit: str = ""
    description: str = ""
    min_value: float = 0.0
    max_value: float = 1000.0


class RacelogicParser:
    """
    Backward‑compatible parser shell.

    Actual data comes from the DBC database.  The `.parameters` list
    is populated lazily from the matching DBC vehicle entry.
    """

    def __init__(self):
        self.header: Dict[str, Any] = {}
        self.parameters: List[RacelogicParameter] = []
        self.decompressed_data: Optional[bytes] = None
        self._manufacturer: str = ""
        self._model: str = ""

    def parse_file(self, file_path: Path) -> bool:
        """Match REF filename to DBC vehicle and load signals."""
        stem = file_path.stem  # "BMW-M3 (F80) 2014-2019"

        # Try known multi‑word manufacturers first
        multi = {
            "Alfa Romeo", "Aston Martin", "Chevrolet", "Citroen",
            "Land Rover", "Mercedes", "Rolls Royce", "Range Rover",
            "Vauxhall", "Volkswagen",
        }
        for m in multi:
            if stem.startswith(m + "-"):
                self._manufacturer = m
                self._model = stem[len(m) + 1:]
                break
        else:
            # Single‑word manufacturer: split on first hyphen only
            #  "Audi-A4 (B8) 2007 - 2015" → ("Audi", "A4 (B8) 2007 - 2015")
            if "-" in stem:
                parts = stem.split("-", 1)
                self._manufacturer = parts[0].strip()
                self._model = parts[1].strip()
            else:
                self._manufacturer = stem
                self._model = ""


        db = get_database()
        vdb = db.vehicle(self._manufacturer, self._model)

        if vdb is None:
            logger.warning("No DBC vehicle found for '%s' — returning empty", file_path.name)
            return False

        self.header = {
            "version": "DBC",
            "source": str(file_path.name),
            "dbc_vehicle": f"{vdb.manufacturer} {vdb.model}",
        }

        self.parameters.clear()
        for can_id, msg in vdb.messages.items():
            for sig in msg.signals:
                self.parameters.append(RacelogicParameter(
                    name=sig.name,
                    can_id=can_id,
                    channel=(can_id >> 8) & 0x0F,
                    conversion_factor=sig.scale,
                    conversion_offset=sig.offset,
                    unit=sig.unit,
                    description=f"CAN ID 0x{can_id:03X} — {vdb.manufacturer} {vdb.model}",
                    min_value=sig.min_value,
                    max_value=sig.max_value,
                ))

        logger.info(
            "DBC-backed: %d parameters for %s %s",
            len(self.parameters), self._manufacturer, self._model,
        )
        return True

    def get_parameters_dict(self) -> Dict[str, RacelogicParameter]:
        return {f"{p.name}": p for p in self.parameters}


def parse_racelogic_ref_file(file_path: Path) -> Optional[RacelogicParser]:
    """
    Parse a Racelogic .REF file (DBC‑backed) and return parser instance.

    NOTE: The original REF binary file is no longer used.
    Signal data is served from the DACOS DBC database.
    """
    parser = RacelogicParser()
    if parser.parse_file(file_path):
        return parser
    return None
