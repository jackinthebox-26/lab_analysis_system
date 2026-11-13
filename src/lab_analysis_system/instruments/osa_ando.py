import logging
from pathlib import Path

import pandas as pd

from lab_analysis_system.instrument_base import Instrument
from lab_analysis_system.instrument_tools import parse_OSC_settings, parse_spect_data, analyze_spectrum, plot_spect_row_w_fit

logger = logging.getLogger(__name__)

class OSAAndo(Instrument):
    
    @property
    def name(self) -> str:
        return "osa_ando"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return ",dBm" in first_5_lines[0]  # Note that it always outputs this even when saving in linear

    def parse(self, file_path):
        meta_data = {"source_file": file_path.name}
        meta_data |= parse_OSC_settings(file_path.name)
        meta_data |= parse_spect_data(str(file_path))
        return meta_data
    
    def analyze(self, raw_data: dict) -> dict:
        processed_data = {}
        processed_data |= raw_data
        processed_data = analyze_spectrum(processed_data)
        return processed_data

    def plot(self, row: pd.Series, figure_dir: str | Path | None = None) -> None:
            """Render and save the default diagnostic plot for one processed data row."""
            plot_spect_row_w_fit(row, self.name, figure_dir)

    