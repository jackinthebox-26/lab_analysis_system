import logging
from pathlib import Path

from lab_analysis_system.instrument_base import Instrument

logger = logging.getLogger(__name__)

class SpectAurora4000(Instrument):
    
    @property
    def name(self) -> str:
        return "spect_aurora_4000"

    @property
    def config_key(self) -> str:
        return "spect_aurora_4000"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return "Device Name:Aurora 4000" in first_5_lines[4]