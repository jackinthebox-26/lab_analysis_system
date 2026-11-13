import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

import logging

from datetime import datetime

from lab_analysis_system.config import RAW_DIR, FIG_CONFIG, FIGURE_PATH, DATA_LOAD_CONFIG
from lab_analysis_system.math_tools import fit_gaussian_profile, gaussian, FWHM_to_stddev

logger = logging.getLogger(__name__)

BBOX_PROPS = dict(
                boxstyle=FIG_CONFIG['info_box']['boxstyle'],  # Options: 'square', 'round', 'sawtooth'
                facecolor=FIG_CONFIG['info_box']['facecolor'],         # Background fill color
                edgecolor=FIG_CONFIG['info_box']['edgecolor'],          # Border line color
                alpha=FIG_CONFIG['info_box']['alpha'],                 # Transparency (0 to 1)
                linewidth=FIG_CONFIG['info_box']['linewidth']
            )

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

def analyze_spectrum(data_pd):
    fit_dict = fit_gaussian_profile(
        data_pd['Wavelength (nm)'],
        data_pd['Power (mW)']
    )

    data_pd['Center Wavelength (nm)'] = fit_dict['center']
    data_pd['FWHM Wavelength (nm)'] = fit_dict['fwhm']
    data_pd['amplitude'] = fit_dict['amplitude']
    data_pd['offset'] = fit_dict['offset']

    power = np.asarray(data_pd['Power (mW)'], dtype=float)
    offset = fit_dict['offset'] if not np.isnan(fit_dict['offset']) else np.min(power)
    shifted = power - offset
    max_val = np.max(shifted)
    norm_power = shifted / max_val if max_val > 0 else shifted

    data_pd['Normalized Linear Power (a.u.)'] = norm_power.tolist()
    return data_pd

def add_info_box(ax, text_dict, x=0.03, y=-0.4):
    ax.text(
                x, y,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
                text_dict,
                transform=ax.transAxes,    # Coordinates relative to axes, not data values
                fontsize=FIG_CONFIG['info_box']['fontsize'],
                fontfamily=FIG_CONFIG['info_box']['fontfamily'],    # Monospace keeps key-value pairs aligned
                verticalalignment=FIG_CONFIG['info_box']['verticalalignment'],
                horizontalalignment=FIG_CONFIG['info_box']['horizontalalignment'],
                bbox=BBOX_PROPS
            )
    return ax

def save_and_close_plot(config_key, source_file):
    clean_source = str(source_file).strip().replace('\r', '').replace('\n', '')
    plot_folder = (FIGURE_PATH / DATA_LOAD_CONFIG[config_key]['plot_folder']).resolve()

    plot_folder.mkdir(parents=True, exist_ok=True)

    plt.tight_layout()
    output_filename = plot_folder / f"plot_{Path(clean_source).stem}.png"
    plt.savefig(output_filename)
    logger.info(f"Saved graph to {output_filename}")
    plt.close()

def plot_spect_row(row: pd.Series, config_key: str):
    template = FIG_CONFIG[config_key]['file_info']
    file_info = template.format(**row)
    fig, ax = plt.subplots(1, 1)
    ax.plot(row["Wavelength (nm)"], 
                row["Normalized Linear Power (a.u.)"], 
                label='Data',
                color=FIG_CONFIG['default_fig_settings']['color'])
    ax.set_xlabel(FIG_CONFIG[config_key]['xlabel'])
    ax.set_ylabel(FIG_CONFIG[config_key]['ylabel'])


    plt.suptitle(f"{row['source_file']}")
    ax = add_info_box(ax, file_info)
    
    save_and_close_plot(config_key, row['source_file']) 

def plot_spect_row_w_fit(row: pd.Series, config_key: str):
    template = FIG_CONFIG[config_key]['file_info']
    file_info = template.format(**row)
    fig, ax = plt.subplots(1, 2)
    ax[0].plot(row["Wavelength (nm)"], 
                row["Normalized Linear Power (a.u.)"], 
                label='Data',
                color=FIG_CONFIG['default_fig_settings']['color'])
    ax[0].set_xlabel(FIG_CONFIG[config_key]['xlabel'])
    ax[0].set_ylabel(FIG_CONFIG[config_key]['ylabel'])


    plt.suptitle(f"{row['source_file']}")
    ax[0] = add_info_box(ax[0], file_info)


    ax[1].plot(row["Wavelength (nm)"], 
                row["Normalized Linear Power (a.u.)"], 
                label='Data',
                color=FIG_CONFIG['default_fig_settings']['color'])
    ax[1].plot(row['Wavelength (nm)'], gaussian(row['Wavelength (nm)'], 
                                                1, 
                                                row['Center Wavelength (nm)'],
                                                FWHM_to_stddev(row['FWHM Wavelength (nm)']),
                                                0),
                                                color=FIG_CONFIG['gaussian_plot']['color'],
                                                linestyle=FIG_CONFIG['gaussian_plot']['linestyle'],
                                                label=FIG_CONFIG['gaussian_plot']['label'])

    ax[1].set_xlabel(FIG_CONFIG[config_key]['xlabel'])
    ax[1].set_ylabel(FIG_CONFIG[config_key]['ylabel'])

    center_wavelength = row['Center Wavelength (nm)']
    fwhm = row['FWHM Wavelength (nm)']

    window = FIG_CONFIG['default_fig_settings']['tight_plot_window']

    if np.isnan(center_wavelength) or np.isnan(fwhm):
        logger.warning(f"Warning: Center wavelength or FWHM is NaN for {row['source_file']}. Skipping xlim setting.")
    else:
        ax[1].set_xlim([center_wavelength - fwhm * window,
                        center_wavelength + fwhm * window]) 
    
    ax[1].legend()
    
    save_and_close_plot(config_key, row['source_file']) 