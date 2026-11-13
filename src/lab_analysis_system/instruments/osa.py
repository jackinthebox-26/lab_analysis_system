import logging

from lab_analysis_system.instrument_base import Instrument

logger = logging.getLogger(__name__)

class OpticalSpectrumAnalyzer(Instrument):
    
    @property
    def name(self) -> str:
        return "OSA"