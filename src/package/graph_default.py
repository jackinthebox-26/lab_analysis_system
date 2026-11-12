from pathlib import Path
import logging

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from package.config import DATA_LOAD_CONFIG, FIG_CONFIG, PROCESSED_DATA_PATH, FIGURE_PATH
from package.math_tools import gaussian, FWHM_to_stddev

logger = logging.getLogger(__name__)

BBOX_PROPS = dict(
                boxstyle=FIG_CONFIG['info_box']['boxstyle'],  # Options: 'square', 'round', 'sawtooth'
                facecolor=FIG_CONFIG['info_box']['facecolor'],         # Background fill color
                edgecolor=FIG_CONFIG['info_box']['edgecolor'],          # Border line color
                alpha=FIG_CONFIG['info_box']['alpha'],                 # Transparency (0 to 1)
                linewidth=FIG_CONFIG['info_box']['linewidth']
            )

def load_data(config_key):

    file_path = PROCESSED_DATA_PATH / DATA_LOAD_CONFIG[config_key]['data_file']
    logger.info(file_path)
    logger.info(f"Loading data from {file_path}")
    if not file_path.is_file():
        return None
    data = pd.read_json(file_path)
    return data


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

def plot_spectra(config_key):
    data = load_data(config_key)
    if data is None:
        logger.info(f"No {config_key.replace('_', ' ')} ")
        return
    for index, row in data.iterrows():
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


def plot_OSA_data():
    config_key = 'OSA_data'
    plot_spectra(config_key)

def plot_RF_data():
    config_key = 'RF_data'
    data = load_data(config_key)
    if data is None:
            logger.info("No RF data")
            return
    for index, row in data.iterrows():
        template = FIG_CONFIG['RF_data']['file_info']
        file_info = template.format(**row)
        
        fig, ax = plt.subplots(figsize=FIG_CONFIG['default_fig_settings']['figsize'], 
                               dpi=FIG_CONFIG['default_fig_settings']['dpi'])
        ax.plot(np.array(row['Frequency (Hz)']) * 1e-6, row['Power (dBm)'],
                   color=FIG_CONFIG['default_fig_settings']['color'])

      
        ax.set_xlabel(FIG_CONFIG['RF_data']['xlabel'])
        ax.set_ylabel(FIG_CONFIG['RF_data']['ylabel'])
        plt.suptitle(f"RF Data - {row['date']}")
        ax = add_info_box(ax, file_info)
        save_and_close_plot(config_key, row['source_file'])
        
def plot_aurora_data():
    config_key = 'aurora_data'
    plot_spectra(config_key)

def plot_ocean_optics_data():
    config_key = 'ocean_optics_data'
    plot_spectra(config_key)

def plot_FROG_data():
    
    config_key = 'FROG_data'
    data = load_data(config_key)
    if data is None:
        logger.info("No FROG data")
        return
    for index, row in data.iterrows():
        template = FIG_CONFIG['FROG_data']['file_info']
        file_info = template.format(**row)
      
        
        fig, ax = plt.subplots(1, 3, figsize=FIG_CONFIG['default_fig_settings']['figsize'], 
                               dpi=FIG_CONFIG['default_fig_settings']['dpi'])

        ax[0].plot(np.array(row["pulse_time_data_time"]), np.array(row["pulse_time_data_intensity"]))
        ax[0].set_xlabel('Time (fs)')
        ax[0].set_ylabel('Normalized Linear Power (a.u.)')
        plt.suptitle(f"Pulse temporal data \n{row['source_file']}")

        ax[1].plot(np.array(row["pulse_freq_data_wavelength"]), np.array(row["pulse_freq_data_intensity"]))
        ax[1].set_xlabel('Wavelength (nm)')
        ax[1].set_ylabel('Normalized Linear Power (a.u.)')
        
        
        ax[2] = add_info_box(ax[2], file_info)
        ax[2].set_axis_off()
        
        save_and_close_plot(config_key, row['source_file'])

def create_all_graphs():
    logger.info("-------------------Initializing plot creation-------------------")
    logger.info("Creating OSA graphs")
    plot_OSA_data()
    logger.info("Creating RF analyser graphs")
    plot_RF_data()
    logger.info("Creating Aurora 4000 graphs")
    plot_aurora_data()
    logger.info("Creating Ocean Optics graphs")
    plot_ocean_optics_data()
    logger.info("Creating FROG graphs")
    plot_FROG_data()
    logger.info("Completed graph creation")

    

if __name__ == "__main__":
    create_all_graphs()
