from pathlib import Path
from datetime import datetime
import tomllib

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import git




BASE_DIR = Path(__file__).resolve().parent.parent.parent
config_path = BASE_DIR / 'config' / 'data_load_config.toml'

plt.style.use(BASE_DIR / 'config' / 'plot_style.mplstyle')

config_path = Path(config_path)
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

fig_config_path = BASE_DIR / 'config' / 'figure_config.toml'

fig_config_path = Path(fig_config_path)
with open(fig_config_path, 'rb') as f:
    fig_config = tomllib.load(f)


RAW_DIR = Path(config['raw_data']['raw_data_folder'])

PROCESSED_TEMP_DATA_PATH = Path(config['processed_data']['processed_data_folder'])
FIGURE_TEMP_PATH = Path(config['processed_data']['plot_data_folder'])


if config['processed_data']['store_processed_with_data']:
    PROCESSED_DATA_PATH = BASE_DIR / RAW_DIR / PROCESSED_TEMP_DATA_PATH
else:
    PROCESSED_DATA_PATH = BASE_DIR / PROCESSED_TEMP_DATA_PATH
     


if config['processed_data']['store_plots_with_data']:
    FIGURE_PATH = BASE_DIR / RAW_DIR / FIGURE_TEMP_PATH
else:
    PROCESSED_DATA_PATH = BASE_DIR / PROCESSED_TEMP_DATA_PATH



BBOX_PROPS = dict(
                boxstyle=fig_config['info_box']['boxstyle'],  # Options: 'square', 'round', 'sawtooth'
                facecolor=fig_config['info_box']['facecolor'],         # Background fill color
                edgecolor=fig_config['info_box']['edgecolor'],          # Border line color
                alpha=fig_config['info_box']['alpha'],                 # Transparency (0 to 1)
                linewidth=fig_config['info_box']['linewidth']
            )


def gaussian(x, amplitude, mean, stddev, offset):
    """1D Gaussian model with a baseline offset."""
    x = np.hstack(x).astype(float)
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset

def FWHM_to_stddev(FWHM):
    return (1 / (2 * np.sqrt(2 * np.log(2)))) * FWHM

def load_data(config_key):

    file_path = PROCESSED_DATA_PATH / config[config_key]['data_file']
    print(file_path)
    print(f"Loading data from {file_path}")
    if not file_path.is_file():
        return None
    data = pd.read_json(file_path)
    return data


def add_info_box(ax, text_dict, x=0.03, y=-0.4):
    ax.text(
                x, y,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
                text_dict,
                transform=ax.transAxes,    # Coordinates relative to axes, not data values
                fontsize=fig_config['info_box']['fontsize'],
                fontfamily=fig_config['info_box']['fontfamily'],    # Monospace keeps key-value pairs aligned
                verticalalignment=fig_config['info_box']['verticalalignment'],
                horizontalalignment=fig_config['info_box']['horizontalalignment'],
                bbox=BBOX_PROPS
            )
    return ax


def save_and_close_plot(config_key, source_file):
    plot_folder = FIGURE_PATH / config[config_key]['plot_folder']

    plot_folder.mkdir(parents=True, exist_ok=True)

    plt.tight_layout()
    output_filename = plot_folder / f"plot_{Path(source_file).stem}.png"
    plt.savefig(output_filename)
    print(f"Saved graph to {output_filename}")
    plt.close()



def plot_OSA_data():
    config_key = 'OSA_data'
    data = load_data(config_key)
    if data is None:
            print("No OSA data")
            return
    for index, row in data.iterrows():
        template = fig_config['OSA_plot']['file_info']
        file_info = template.format(**row)
        
        fig, ax = plt.subplots(1, 2)
        ax[0].plot(row["Wavelength (nm)"], 
                   row["Normalized Power (mW)"], 
                   label='Data',
                   color=fig_config['default_fig_settings']['color'])

        
        ax[0].set_xlabel(fig_config['OSA_plot']['xlabel'])
        ax[0].set_ylabel(fig_config['OSA_plot']['ylabel'])
        ax[0].legend()


        plt.suptitle(f"OSA Data - {row['date']}")
        ax[0] = add_info_box(ax[0], file_info)


        ax[1].plot(row["Wavelength (nm)"], 
                   row["Normalized Power (mW)"], 
                   label='Data',
                   color=fig_config['default_fig_settings']['color'])
        ax[1].plot(row['Wavelength (nm)'], gaussian(row['Wavelength (nm)'], 
                                                    1, 
                                                    row['Center Wavelength (nm)'],
                                                    FWHM_to_stddev(row['FWHM Wavelength (nm)']),
                                                    0),
                                                    color=fig_config['gaussian_plot']['color'],
                                                    linestyle=fig_config['gaussian_plot']['linestyle'],
                                                    label=fig_config['gaussian_plot']['label'])

        ax[1].set_xlabel(fig_config['OSA_plot']['xlabel'])
        ax[1].set_ylabel(fig_config['OSA_plot']['ylabel'])

        center_wavelength = row['Center Wavelength (nm)']
        fwhm = row['FWHM Wavelength (nm)']

        window = config['plot_config']['tight_plot_window']

        ax[1]. set_xlim([center_wavelength - fwhm * window,
                         center_wavelength + fwhm * window])
        
        
        save_and_close_plot(config_key, row['source_file'])
        

def plot_RF_data():
    config_key = 'RF_data'
    data = load_data(config_key)
    if data is None:
            print("No RF data")
            return
    for index, row in data.iterrows():
        template = fig_config['RF_plot']['file_info']
        file_info = template.format(**row)
        
        fig, ax = plt.subplots(figsize=fig_config['default_fig_settings']['figsize'], 
                               dpi=fig_config['default_fig_settings']['dpi'])
        ax.plot(np.array(row['Frequency (Hz)']) * 1e-6, row['Power (dBm)'],
                   color=fig_config['default_fig_settings']['color'])

      
        ax.set_xlabel(fig_config['RF_plot']['xlabel'])
        ax.set_ylabel(fig_config['RF_plot']['ylabel'])
        plt.suptitle(f"RF Data - {row['date']}")
        ax = add_info_box(ax, file_info)
        save_and_close_plot(config_key, row['source_file'])
        
def plot_aurora_data():
    
    config_key = 'aurora_data'
    data = load_data(config_key)
    if data is None:
            print("No Aurora data")
            return

    for index, row in data.iterrows():
        
        template = fig_config['aurora_plot']['file_info']
        file_info = template.format(**row)
        
        fig, ax = plt.subplots(1, 2, figsize=fig_config['default_fig_settings']['figsize'],
                               dpi=fig_config['default_fig_settings']['dpi'])
        ax[0].plot(np.array(row[f"Wavelength ({row['X-Axis Unit']})"]), 
                   np.array(row[f"Normalized Power (mW)"]),
                   color=fig_config['default_fig_settings']['color'])
       
                


        ax[0].set_xlabel('Wavelength (nm)')
        ax[0].set_ylabel('Normalized Power (mW)')
        plt.suptitle(f"Aurora 4000 Data - {row['source_file']}")

        ax[1].plot(np.array(row[f"Wavelength ({row['X-Axis Unit']})"]), 
                   np.array(row[f"Normalized Power (mW)"]),
                   color=fig_config['default_fig_settings']['color'])
        ax[1].plot(row['Wavelength (nm)'], gaussian(row['Wavelength (nm)'], 
                                                            1, 
                                                            row['Center Wavelength (nm)'],
                                                            FWHM_to_stddev(row['FWHM Wavelength (nm)']),
                                                            0),
                                                            color=fig_config['gaussian_plot']['color'],
                                                            linestyle=fig_config['gaussian_plot']['linestyle'],
                                                            label=fig_config['gaussian_plot']['label'])
                


        ax[1].set_xlabel(fig_config['aurora_plot']['xlabel'])
        ax[1].set_ylabel(fig_config['aurora_plot']['ylabel'])
        

        center_wavelength = row['Center Wavelength (nm)']
        fwhm = row['FWHM Wavelength (nm)']

        window = config['plot_config']['tight_plot_window']

        ax[1]. set_xlim([center_wavelength - fwhm * window,
                            center_wavelength + fwhm * window])

        ax[0] = add_info_box(ax[0], file_info)
        save_and_close_plot(config_key, row['source_file'])

def plot_ocean_optics_data():
    
    config_key = 'ocean_optics_data'
    data = load_data(config_key)
    if data is None:
            print("No Ocean Optics data")
            return
    for index, row in data.iterrows():
        template = fig_config['ocean_optics_plot']['file_info']
        file_info = template.format(**row)
        fig, ax = plt.subplots(1, 2, figsize=fig_config['default_fig_settings']['figsize'], 
                               dpi=fig_config['default_fig_settings']['dpi'])
        
        plt.suptitle(f"Ocean Optics Data - {row['source_file']}")

        ax[0].plot(np.array(row[f"Wavelength (nm)"]), 
                   np.array(row[f"Normalized Power (mW)"]),
                   color=fig_config['default_fig_settings']['color'])

                
      
     
        ax[0].set_xlabel('Wavelength (nm)')
        ax[0].set_ylabel('Normalized Power (mW)')

        ax[1].plot(np.array(row[f"Wavelength (nm)"]), 
                   np.array(row[f"Normalized Power (mW)"]),
                   color=fig_config['default_fig_settings']['color'])
        ax[1].plot(row['Wavelength (nm)'], gaussian(row['Wavelength (nm)'], 
                                                1, 
                                                row['Center Wavelength (nm)'],
                                                FWHM_to_stddev(row['FWHM Wavelength (nm)']),
                                                0),
                                                color=fig_config['gaussian_plot']['color'],
                                                linestyle=fig_config['gaussian_plot']['linestyle'],
                                                label=fig_config['gaussian_plot']['label'])
        
        
        ax[1].set_xlabel(fig_config['ocean_optics_plot']['xlabel'])
        ax[1].set_ylabel(fig_config['ocean_optics_plot']['ylabel'])
        

        
        center_wavelength = row['Center Wavelength (nm)']
        fwhm = row['FWHM Wavelength (nm)']

        window = config['plot_config']['tight_plot_window']

        ax[1]. set_xlim([center_wavelength - fwhm * window,
                         center_wavelength + fwhm * window])
        
        
        ax[0] = add_info_box(ax[0], file_info)
        save_and_close_plot(config_key, row['source_file'])

def plot_FROG_data():
    
    config_key = 'FROG_data'
    data = load_data(config_key)
    if data is None:
        print("No FROG data")
        return
    for index, row in data.iterrows():
        template = fig_config['ocean_optics_plot']['file_info']
        file_info = template.format(**row)
      
        
        fig, ax = plt.subplots(1, 3, figsize=fig_config['default_fig_settings']['figsize'], 
                               dpi=fig_config['default_fig_settings']['dpi'])

        ax[0].plot(np.array(row["pulse_time_data_time"]), np.array(row["pulse_time_data_intensity"]))
        ax[0].set_xlabel('Time (fw)')
        ax[0].set_ylabel('Normalized Power (mW)')
        plt.suptitle(f"Pulse temporal data \n{row['source_file']}")

        ax[1].plot(np.array(row["pulse_freq_data_frequency"]), np.array(row["pulse_freq_data_intensity"]))
        ax[1].set_xlabel('Wavelength (nm)')
        ax[1].set_ylabel('Normalized Power (mW)')
        
    
        
        ax[2] = add_info_box(ax[2], file_info)
        ax[2].set_axis_off()
        
        save_and_close_plot(config_key, row['source_file'])

def create_all_graphs():
    print("-------------------Initializing plot creation-------------------")
    print("Creating OSA graphs")
    plot_OSA_data()
    print("Creating RF analyser graphs")
    plot_RF_data()
    print("Creating Aurora 4000 graphs")
    plot_aurora_data()
    print("Creating Ocean Optics graphs")
    plot_ocean_optics_data()
    print("Creating FROG graphs")
    plot_FROG_data()
    print("Completed graph creation")

    

if __name__ == "__main__":
    create_all_graphs()
