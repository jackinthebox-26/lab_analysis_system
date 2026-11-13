import logging
from pathlib import Path

from lab_analysis_system.instrument_base import Instrument

logger = logging.getLogger(__name__)

class OSAAndo(Instrument):
    
    @property
    def name(self) -> str:
        return "osa_ando"

    @property
    def config_key(self) -> str:
        return "OSA_data"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return ",dBm" in first_5_lines[0]