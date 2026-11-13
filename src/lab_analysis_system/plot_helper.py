# src/package/plot_helpers.py
from pathlib import Path
import numpy as np
import pandas as pd
import logging
from lab_analysis_system.config import DATA_LOAD_CONFIG, PROCESSED_DATA_PATH
from lab_analysis_system.math_tools import gaussian, FWHM_to_stddev
from lab_analysis_system.instrument_base import Instrument
import lab_analysis_system.instruments


logger = logging.getLogger(__name__)

def load_all_data() -> dict[str, pd.DataFrame]:
    loaded_data: dict[str, pd.DataFrame] = {}
    for inst in Instrument.get_all_instruments():
        cfg = DATA_LOAD_CONFIG.get(inst.name)
        if not cfg or "data_file" not in cfg:
            continue
        path = PROCESSED_DATA_PATH / cfg["data_file"]
        if path.is_file():
            temp_df = pd.read_json(path)
            for col in temp_df.columns:
                if len(temp_df) > 0 and isinstance(temp_df[col].iloc[0], list):
                    temp_df[col] = temp_df[col].apply(np.array)
            loaded_data[inst.name] = temp_df
    return loaded_data

def inspect_data_files(data_dict: dict[str, pd.DataFrame]) -> None:
    for name, df in data_dict.items():
        logger.info(f"-- {name.upper()} data ({len(df)} rows) --")
        logger.info(df.columns.tolist())

def plot_spectrum_with_fit(ax, row: pd.Series, color: str, data_label: str) -> None:
    wl = row["Wavelength (nm)"]
    pwr = row["Normalized Linear Power (a.u.)"]
    center = row["Center Wavelength (nm)"]
    fwhm = row["FWHM Wavelength (nm)"]

    ax.plot(wl, pwr, color=color, label=data_label)
    if not (np.isnan(center) or np.isnan(fwhm)):
        fit_y = gaussian(wl, 1, center, FWHM_to_stddev(fwhm), 0)
        ax.plot(
            wl, fit_y, color="black", alpha=0.5, linestyle="--",
            label=rf"Fit: $\lambda_0$ = {center:.2f} nm, FWHM = {fwhm:.2f} nm",
        )