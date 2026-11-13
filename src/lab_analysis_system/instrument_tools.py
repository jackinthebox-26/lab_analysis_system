import pandas as pd
import numpy as np
from pathlib import Path

from datetime import datetime

from lab_analysis_system.config import RAW_DIR

def _parse_delimited_spectrum(file_path: Path, start_marker: str) -> dict:
    data_start_line = 0
    data = {'source_file': file_path.name}
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f):
            line_str = line.strip()
            if start_marker in line_str:
                data_start_line = idx + 1
                break
            if ":" in line_str:
                key, value = line_str.split(":", 1)
                data[key.strip()] = value.strip()

    spectral_data = pd.read_csv(
        file_path, sep=r"\s+", on_bad_lines="skip",
        skiprows=data_start_line, header=None,
        names=["Wavelength (nm)", "Power (mW)"],
    )
    data["Wavelength (nm)"] = spectral_data["Wavelength (nm)"].tolist()
    data["Power (mW)"] = spectral_data["Power (mW)"].tolist()
    return data



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

def parse_spect_data(file_path, header=None, skiprows=1):
    data = pd.read_csv(file_path, header=header, skiprows=skiprows)
    data.columns = ["Wavelength (nm)", "Power (mW)"]

    meta_data = {}
    meta_data["Wavelength (nm)"] = data["Wavelength (nm)"].tolist()
    meta_data["Power (mW)"] = data["Power (mW)"] .tolist()
    return meta_data