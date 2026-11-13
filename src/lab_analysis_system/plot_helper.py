# src/package/plot_helpers.py
from pathlib import Path
import numpy as np
import pandas as pd
import logging
from lab_analysis_system.config import DATA_LOAD_CONFIG, PROCESSED_DATA_PATH
from lab_analysis_system.math_tools import gaussian, FWHM_to_stddev


logger = logging.getLogger(__name__)

def load_all_data() -> dict[str, pd.DataFrame]:
    data_sources = {
        "osa": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG["OSA_data"]["data_file"],
        "rf": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG["RF_data"]["data_file"],
        "aurora": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG["aurora_data"]["data_file"],
        "ocean_optics": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG["ocean_optics_data"]["data_file"],
        "frog": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG["FROG_data"]["data_file"],
    }
    loaded_data: dict[str, pd.DataFrame] = {}
    for key, path in data_sources.items():
        if Path(path).exists():
            temp_df = pd.read_json(path)
            for col in temp_df.columns:
                if len(temp_df) > 0 and isinstance(temp_df[col].iloc[0], list):
                    temp_df[col] = temp_df[col].apply(np.array)
            loaded_data[key] = temp_df
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