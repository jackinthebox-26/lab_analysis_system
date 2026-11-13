import pandas as pd

def _parse_delimited_spectrum(file_path, start_marker: str) -> dict:
    data_start_line = 0
    data = {}
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