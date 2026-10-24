import pandas as pd
import numpy as np
import re
from datetime import datetime


def parse_OSA(file_path: str, header_1: str = 'Wavelength (nm)', header_2: str = 'Power (mW)') -> pd.DataFrame:
    meta_data = {
            "source_file": file_path.name,
        }
    data = pd.read_csv(file_path, header=None, skiprows=1)
    data.columns = [header_1, header_2]


    tokens = file_path.name.split('_')
    meta_data['exp_index'] = tokens.pop(0) 
    time = tokens.pop().split('.')[0]
    date = tokens.pop()
    
    meta_data['date'] = datetime.strptime(f"{date}{time}" , "%Y%m%d%H%M%S").isoformat()
    removed_tokens = np.zeros(len(tokens), dtype=int)
    
    i = 0
    for i in range(len(tokens)):
        token = tokens[i]
        match=True
        if token == 'HWP2' and i + 1 < len(tokens):
            meta_data['HWP2'] = float(tokens[i+1].replace('dot', '.'))
        elif token == 'HWP1' and i + 1 < len(tokens):
            meta_data['HWP1'] = float(tokens[i+1].replace('dot', '.'))
        elif token == 'QWP' and i + 1 < len(tokens):
            meta_data['QWP'] = float(tokens[i+1].replace('dot', '.'))
        elif token.endswith('mA'):
            meta_data['Pump current'] = token.removesuffix('mA').replace('dot', '.') 
            removed_tokens[i] = 1
            match = False
        else:
            match = False

        if match:
            removed_tokens[i] = 1
            removed_tokens[i+1] = 1
    notes_list = [token for token, mask in zip(tokens, removed_tokens) if mask == 0]
    meta_data['Notes'] = " ".join(notes_list)

    
    meta_data[header_1] = tuple(data[header_1].tolist())
    meta_data[header_2] = tuple(data[header_2].tolist())
    return meta_data

def parse_aurora_4000(file_path: str) -> pd.DataFrame:
    meta_data = {
        "source_file": file_path.name,
    }

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

def parse_ocean_optics(file_path: str) -> pd.DataFrame:
    meta_data = {
            "source_file": file_path.name,
        }
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

def parse_RF_analyser(file_path: str) -> pd.DataFrame:
    meta_data = {
                "source_file": file_path.name,
            }

    
    tokens = file_path.name.split('_')
    meta_data['exp_index'] = tokens.pop(0) 
    tokens[-1] = tokens[-1].split('.')[0]
    removed_tokens = np.zeros(len(tokens), dtype=int)
    
    remaining_tokens = tokens[:]
    
    i = 0
    for i in range(len(tokens)):
        token = tokens[i]
        match=True
        if token == 'HWP2' and i + 1 < len(tokens):
            meta_data['HWP2'] = float(tokens[i+1].replace('dot', '.'))
        elif token == 'HWP1' and i + 1 < len(tokens):
            meta_data['HWP1'] = float(tokens[i+1].replace('dot', '.'))
        elif token == 'QWP' and i + 1 < len(tokens):
            meta_data['QWP'] = float(tokens[i+1].replace('dot', '.'))
        elif token.endswith('mA'):
            meta_data['Pump current'] = token.removesuffix('mA').replace('dot', '.') 
            removed_tokens[i] = 1
            match = False
        else:
            match = False
        if match:
            removed_tokens[i] = 1
            removed_tokens[i+1] = 1
    notes_list = [token for token, mask in zip(tokens, removed_tokens) if mask == 0]
    meta_data['Notes'] = " ".join(notes_list)


    
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

    date_macro = meta_data['date__day-month-year']
    time = meta_data['time__24h-minute-second']

    meta_data['date'] = datetime.strptime(date_macro + time, "%d_%m_%Y%H_%M_%S").isoformat()

    return meta_data

def parse_FROG_pulse_stats(file_path: str) -> pd.DataFrame:
    meta_data = {
                    "source_file": file_path.name,
                }

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
        time_match = re.search(r"(?P<month>\d+)\_(?P<day>\d+)\_time\_(?P<h>\d+)\_(?P<m>\d+)\_(?P<s>\d+)\_(?P<ms>\d+)", file_path.stem)
        if time_match:
            t = time_match.groupdict()
            meta_data["timestamp"] = f"2026-{t['month']}-{t['day']} {t['h']}:{t['m']}:{t['s']}.{t['ms']}"

        pulse_time_file = file_path.parent / f"Pulse_Time_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
        pulse_time_data = pd.read_csv(pulse_time_file, header=None, names=['Time (fs)', 'Intensity (a.u.)', 'Empty'], sep=r"\s+")
        meta_data["pulse_time_data_time"] = tuple(pulse_time_data["Time (fs)"].tolist())
        meta_data["pulse_time_data_intensity"] = tuple(pulse_time_data["Intensity (a.u.)"].tolist())

        pulse_complex_time_file = file_path.parent / f"Pulse_Complex_Time_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
        pulse_complex_time_data = pd.read_csv(pulse_complex_time_file, header=None, names=['Time (s)', 'Amplitude (a.u.)', 'Phase (rad)'], sep=r"\s+")
        
        meta_data["pulse_complex_time_data_time"] = tuple(pulse_complex_time_data["Time (s)"].tolist())
        meta_data["pulse_complex_time_data_amplitude"] = tuple(pulse_complex_time_data["Amplitude (a.u.)"].tolist())
        meta_data["pulse_complex_time_data_phase"] = tuple(pulse_complex_time_data["Phase (rad)"].tolist())

        pulse_freq_file = file_path.parent / f"Pulse_Freq_Domain {time_match['month']}_{time_match['day']}_time_{time_match['h']}_{time_match['m']}_{time_match['s']}_{time_match['ms']}.txt"
        pulse_freq_data = pd.read_csv(pulse_freq_file, header=None, names=['Frequency (THz)', 'Intensity (a.u.)', 'Empty'], sep=r"\s+")
        meta_data["pulse_freq_data_frequency"] = tuple(pulse_freq_data["Frequency (THz)"].tolist())
        meta_data["pulse_freq_data_intensity"] = tuple(pulse_freq_data["Intensity (a.u.)"].tolist())

        
        return meta_data


    