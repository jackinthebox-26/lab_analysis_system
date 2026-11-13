import logging
from pathlib import Path

from lab_analysis_system.instrument_base import Instrument

logger = logging.getLogger(__name__)

class RFAAgilent(Instrument):
    
    @property
    def name(self) -> str:
        return "rfa_agilent"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return "Date (day-month-year)," in first_5_lines[0]