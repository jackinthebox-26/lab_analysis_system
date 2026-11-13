import logging
from pathlib import Path

from lab_analysis_system.instrument_base import Instrument

logger = logging.getLogger(__name__)

class FROGMesa(Instrument):
    
    @property
    def name(self) -> str:
        return "frog_mesa"

    @property
    def config_key(self) -> str:
        return "frog_mesa"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return "Pulse_Stats" in file_path.name