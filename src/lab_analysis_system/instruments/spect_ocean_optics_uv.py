import logging
from pathlib import Path

from lab_analysis_system.instrument_base import Instrument

logger = logging.getLogger(__name__)

class SpectOceanOpticsUV(Instrument):
    
    @property
    def name(self) -> str:
        return "spect_ocean_optics_uv"

    @property
    def config_key(self) -> str:
        return "spect_ocean_optics_uv"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return "Spectrometer: HR600944" in first_5_lines[4]