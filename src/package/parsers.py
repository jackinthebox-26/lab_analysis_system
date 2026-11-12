from pathlib import Path
import tomllib

import pandas as pd
import numpy as np
import re
from datetime import datetime

from package.config import RAW_DIR

REQUIRED_OSC_KEYS = ("HWP1", "HWP2", "QWP", "Pump current")

def _infer_year(file_path: Path) -> int:
        # Try to extract a 4-digit year from RAW_DIR (e.g. '../2026/11/03')
        for part in RAW_DIR.resolve().parts:
            if part.isdigit() and len(part) == 4:
                return int(part)
        # Fallback to file modification year
        return datetime.fromtimestamp(file_path.stat().st_mtime).year

def parse_OSC_settings(filename: str, has_timestamp: bool = True) -> dict:
    stem = Path(filename).stem
    tokens = stem.split('_')
    settings = {'exp_index': int(tokens.pop(0))}
    
    if has_timestamp:
        time = tokens.pop()
        date = tokens.pop()
        settings['date'] = datetime.strptime(f"{date}{time}", "%Y%m%d%H%M%S").isoformat()
        

    removed_tokens = np.zeros(len(tokens), dtype=int)
    for i, token in enumerate(tokens):
        if token in ('HWP1', 'HWP2', 'QWP') and i + 1 < len(tokens):
            settings[token] = float(tokens[i + 1].replace('dot', '.'))
            removed_tokens[i] = 1
            removed_tokens[i + 1] = 1
        elif token.endswith('mA'):
            settings['Pump current'] = token.removesuffix('mA').replace('dot', '.')
            removed_tokens[i] = 1

    notes_list = [token for token, mask in zip(tokens, removed_tokens) if mask == 0]
    settings['Notes'] = " ".join(notes_list)

    missing = [k for k in REQUIRED_OSC_KEYS if k not in settings]
    if missing:
        raise ValueError(
            f"Filename '{filename}' is missing required experimental settings: {missing}"
        )

    return settings


class data_parser:
    def __init__(self, file_path, data_type):
        self.file_path = file_path
        self.data_type = data_type
        self.data: dict[str, str | float | list] = {
            "source_file": file_path.name,
        }
        match data_type:
            case 'OSA':
                self.data = self.parse_OSA()
            case 'Aurora 4000':
                self.data = self.parse_aurora_4000()
            case 'Ocean Optics':
                self.data = self.parse_ocean_optics()
            case 'RF analyser':
                self.data = self.parse_RF_analyser()
            case 'FROG pulse stats':
                self.data = self.parse_FROG_pulse_stats()
            case _:
                print(f'Data not extracted from {file_path.name}')



    def parse_OSA(self):
        meta_data = self.data
        meta_data |= parse_OSC_settings(self.file_path.name)

        header_1 = 'Wavelength (nm)'
        header_2 = 'Power (mW)'

        data = pd.read_csv(self.file_path, header=None, skiprows=1)
        data.columns = [header_1, header_2] 
        
        meta_data[header_1] = data[header_1].tolist()
        meta_data[header_2] = data[header_2].tolist()
        return meta_data

    def parse_aurora_4000(self):
        file_path = self.file_path
        meta_data = self.data
        data_start_line = 0

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            line_str = line.strip()
            if ':' in line_str:
                key, value = line_str.split(':', 1)
                meta_data[key.strip()] = value.strip()
            elif "+++++Begin Spectral Data+++++" in line_str:
                data_start_line = idx + 1
                break

        # Parse the spectral data
        spectral_data = pd.read_csv(file_path, sep=r"\s+", on_bad_lines="skip", skiprows=data_start_line, header=None, names=['Wavelength (nm)', 'Power (mW)'])
        meta_data['Wavelength (nm)'] = spectral_data['Wavelength (nm)'].tolist()
        meta_data['Power (mW)'] = spectral_data['Power (mW)'].tolist()
        
        return meta_data

    def parse_ocean_optics(self):
        file_path = self.file_path
        meta_data = self.data
        data_start_line = 0
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            line_str = line.strip()
            if ':' in line_str:
                key, value = line_str.split(':', 1)
                meta_data[key.strip()] = value.strip()
            elif ">>>>>Begin Spectral Data<<<<<" in line_str:
                data_start_line = idx + 1
                break

        # Parse the spectral data
        spectral_data = pd.read_csv(file_path, sep=r"\s+", on_bad_lines="skip", skiprows=data_start_line, header=None, names=['Wavelength (nm)', 'Power (mW)'])
        meta_data['Wavelength (nm)'] = spectral_data['Wavelength (nm)'].tolist()
        meta_data['Power (mW)'] = spectral_data['Power (mW)'].tolist()
        return meta_data

    def parse_RF_analyser(self):
        file_path = self.file_path
        meta_data = self.data

        meta_data |= parse_OSC_settings(self.file_path.name, has_timestamp=False)
        
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
        time = str(meta_data['time__24h-minute-second'])

        meta_data['date'] = datetime.strptime(date_macro + time, "%d_%m_%Y%H_%M_%S").isoformat()

        return meta_data

    def parse_FROG_pulse_stats(self):
        file_path = self.file_path
        meta_data = self.data
        year = _infer_year(file_path)
        # Parse key-value lines
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
            pulse_time_data = pd.read_csv(pulse_time_file, header=None, names=['Time (fs)', 'Intensity (a.u.)', 'Empty'], sep=r"\s+")
            meta_data["pulse_time_data_time"] = pulse_time_data["Time (fs)"].tolist()
            meta_data["pulse_time_data_intensity"] = pulse_time_data["Intensity (a.u.)"].tolist()

            pulse_complex_time_file = file_path.parent / f"Pulse_Complex_Time_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
            pulse_complex_time_data = pd.read_csv(pulse_complex_time_file, header=None, names=['Time (s)', 'Amplitude (a.u.)', 'Phase (rad)'], sep=r"\s+")
            
            meta_data["pulse_complex_time_data_time"] = pulse_complex_time_data["Time (s)"].tolist()
            meta_data["pulse_complex_time_data_amplitude"] = pulse_complex_time_data["Amplitude (a.u.)"].tolist()
            meta_data["pulse_complex_time_data_phase"] = pulse_complex_time_data["Phase (rad)"].tolist()

            pulse_freq_file = file_path.parent / f"Pulse_Freq_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
            pulse_freq_data = pd.read_csv(pulse_freq_file, header=None, names=['Frequency (THz)', 'Intensity (a.u.)', 'Empty'], sep=r"\s+")
            meta_data["pulse_freq_data_wavelength"] = pulse_freq_data["Frequency (THz)"].tolist()  # Note: This is really wavelength, the FROG software outputs frequency in THz, but it's actually wavelength in nm. This is a known quirk of the FROG software.
            meta_data["pulse_freq_data_intensity"] = pulse_freq_data["Intensity (a.u.)"].tolist()

            
            return meta_data


    