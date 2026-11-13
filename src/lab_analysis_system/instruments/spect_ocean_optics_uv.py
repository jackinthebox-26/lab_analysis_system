import logging
from pathlib import Path

import pandas as pd

from lab_analysis_system.instrument_base import Instrument
from lab_analysis_system.instrument_tools import _parse_delimited_spectrum, analyze_spectrum, plot_spect_row_w_fit

logger = logging.getLogger(__name__)

class SpectOceanOpticsUV(Instrument):
    
    @property
    def name(self) -> str:
        return "spect_ocean_optics_uv"


    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return "Spectrometer: HR600944" in first_5_lines[4]

    def parse(self, file_path):
            return _parse_delimited_spectrum(file_path, '>>>>>Begin Spectral Data<<<<<')


    def analyze(self, raw_data: dict) -> dict:
        processed_data = {}
        processed_data |= raw_data
        processed_data = analyze_spectrum(processed_data)
        return processed_data

    def plot(self, row: pd.Series) -> None:
        """Render and save the default diagnostic plot for one processed data row."""
        plot_spect_row_w_fit(row, self.name)