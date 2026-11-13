import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

from lab_analysis_system.instrument_base import Instrument
from lab_analysis_system.instrument_tools import parse_OSC_settings, plot_spect_row

logger = logging.getLogger(__name__)

class RFAAgilent(Instrument):
    
    @property
    def name(self) -> str:
        return "rfa_agilent"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return "Date (day-month-year)," in first_5_lines[0]

    def parse(self, file_path):
        meta_data = {"source_file": file_path.name}
        meta_data |= parse_OSC_settings(file_path.name, has_timestamp=False)

        power_array = []
        freq_array = []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue

                if line_str.startswith("Power,"):
                    power_array = [float(v) for v in line_str.split(",")[1:] if v.strip()]
                elif line_str.startswith("Frequency,"):
                    freq_array = [float(v) for v in line_str.split(",")[1:] if v.strip()]
                elif "," in line_str:
                        parts = [p.strip() for p in line_str.split(",")]
                        key = (
                            parts[0]
                            .lower()
                            .replace(" ", "_")
                            .replace("(", "_")
                            .replace(")", "")
                            .replace("=", "_")
                        )
                        # Join remaining tokens (handles unit strings like 'Hz', 'sec', 'DBM')
                        meta_data[key] = "_".join([p for p in parts[1:] if p])
        meta_data['Power (dBm)'] = power_array
        meta_data['Frequency (Hz)'] = freq_array

        date_macro = str(meta_data['date__day-month-year'])
        time_str = str(meta_data['time__24h-minute-second'])

        if not date_macro or not time_str:
            raise ValueError(f"Missing date/time header fields in RF file: {file_path.name}")

        meta_data['date'] = datetime.strptime(date_macro + time_str, "%d_%m_%Y%H_%M_%S").isoformat()

        return meta_data
    
    def analyze(self, raw_data: dict) -> dict:
            return raw_data

    def plot(self, row: pd.Series) -> None:
            """Render and save the default diagnostic plot for one processed data row."""
            plot_spect_row(row, self.name)