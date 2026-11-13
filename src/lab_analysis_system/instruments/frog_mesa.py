import logging
from pathlib import Path
import re

import pandas as pd

from lab_analysis_system.instrument_base import Instrument
from lab_analysis_system.instrument_tools import _infer_year

logger = logging.getLogger(__name__)

class FROGMesa(Instrument):
    
    @property
    def name(self) -> str:
        return "frog_mesa"

    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        # From your old data_loader.py get_data_type logic
        return "Pulse_Stats" in file_path.name

    def parse(self, file_path):
        year = _infer_year(file_path)
        # Parse key-value lines
        meta_data = {'source_file': file_path.name}
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_str = line.strip()
                if not line_str or line_str.startswith("~") or line_str == "Pulse Statistics":
                    continue

                if ":" in line_str:
                    key, val = line_str.split(":", 1)
                    key_clean = key.strip().lower().replace(" ", "_")
                    val_str = val.strip()

                    # Extract numerical value and unit if present
                    match = re.match(r"^(?P<num>[-+]?\d*\.?\d+(?:e[-+]?\d+)?)\s*(?P<unit>\w+)?$", val_str, re.IGNORECASE)
                    if match:
                        parsed_val = float(match.group("num"))
                        unit = match.group("unit")
                        
                        # Disambiguate duplicate 'bandwidth' keys by appending unit
                        if key_clean in meta_data and unit:
                            key_clean = f"{key_clean}_{unit.lower()}"
                        elif unit:
                            meta_data[f"{key_clean}_unit"] = unit

                        meta_data[key_clean] = parsed_val
                    else:
                        meta_data[key_clean] = val_str

            # Parse timestamp from filename: Pulse_Stats 10_20_time_15_33_12_717
            pattern = r"(?P<month>\d+)\_(?P<day>\d+)\_time\_(?P<h>\d+)\_(?P<m>\d+)\_(?P<s>\d+)\_(?P<ms>\d+)"
            time_match = re.search(pattern, file_path.stem)
            if not time_match:
                raise ValueError(f"Filename {file_path.name} does not match expected timestamp pattern.")
            t = time_match.groupdict()
            meta_data["timestamp"] = f"{year}-{t['month']}-{t['day']} {t['h']}:{t['m']}:{t['s']}.{t['ms']}"
            

            pulse_time_file = file_path.parent / f"Pulse_Time_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
            pulse_complex_time_file = file_path.parent / f"Pulse_Complex_Time_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
            pulse_freq_file = file_path.parent / f"Pulse_Freq_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
                                    
            for companion in (pulse_time_file, pulse_complex_time_file, pulse_freq_file):
                if not companion.is_file():
                    raise FileNotFoundError(f"Missing companion FROG file: {companion.name}")

            pulse_time_data = pd.read_csv(pulse_time_file, header=None, names=['Time (fs)', 'Intensity (a.u.)', 'Empty'], sep=r"\s+")
            pulse_complex_time_data = pd.read_csv(pulse_complex_time_file, header=None, names=['Time (s)', 'Amplitude (a.u.)', 'Phase (rad)'], sep=r"\s+")
            pulse_freq_data = pd.read_csv(pulse_freq_file, header=None, names=['Frequency (THz)', 'Intensity (a.u.)', 'Empty'], sep=r"\s+")
                                                
            
            meta_data["pulse_time_data_time"] = pulse_time_data["Time (fs)"].tolist()
            meta_data["pulse_time_data_intensity"] = pulse_time_data["Intensity (a.u.)"].tolist()

            
            meta_data["pulse_complex_time_data_time"] = pulse_complex_time_data["Time (s)"].tolist()
            meta_data["pulse_complex_time_data_amplitude"] = pulse_complex_time_data["Amplitude (a.u.)"].tolist()
            meta_data["pulse_complex_time_data_phase"] = pulse_complex_time_data["Phase (rad)"].tolist()

            meta_data["pulse_freq_data_wavelength"] = pulse_freq_data["Frequency (THz)"].tolist()  # Note: This is really wavelength, the FROG software outputs frequency in THz, but it's actually wavelength in nm. This is a known quirk of the FROG software.
            meta_data["pulse_freq_data_intensity"] = pulse_freq_data["Intensity (a.u.)"].tolist()
            
            
            return meta_data

