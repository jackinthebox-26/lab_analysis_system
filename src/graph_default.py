from pathlib import Path
from datetime import datetime
import tomllib

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import git

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = Path(config['raw_data']['raw_data_folder'])
PROCESSED_DATA_PATH = Path(config['processed_data']['processed_data_folder'])
if config['processed_data']['store_processed_with_data'].strip().lower() == "true":
    PROCESSED_DATA_PATH = RAW_DIR / PROCESSED_DATA_PATH

FIGURE_PATH = Path(config['processed_data']['plot_data_folder'])

if config['processed_data']['store_plots_with_data'].strip().lower() == "true":
    FIGURE_PATH = RAW_DIR / FIGURE_PATH

PROCESSED_DATA_PATH  = BASE_DIR / PROCESSED_DATA_PATH
FIGURE_PATH = BASE_DIR / FIGURE_PATH

BBOX_PROPS = dict(
                boxstyle="round,pad=0.5",  # Options: 'square', 'round', 'sawtooth'
                facecolor="wheat",         # Background fill color
                edgecolor="gray",          # Border line color
                alpha=0.8,                 # Transparency (0 to 1)
                linewidth=1.2
            )


def gaussian(x, amplitude, mean, stddev, offset):
    """1D Gaussian model with a baseline offset."""
    x = np.hstack(x).astype(float)
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset

def FWHM_to_stddev(FWHM):
    return 0.424661 * FWHM

def load_data(config_key):

    file_path = PROCESSED_DATA_PATH / config[config_key]['data_file']
    print(file_path)
    print(f"Loading data from {file_path}")
    if not file_path.is_file():
        return None
    data = pd.read_json(file_path)
    return data

def get_repo_version(path=BASE_DIR):
    try:
        repo = git.Repo(path, search_parent_directories=True)
        sha = repo.head.commit.hexsha[:7]
        is_dirty = repo.is_dirty()
        print(is_dirty)
    except git.InvalidGitRepositoryError:
        return "not a git repo"


def add_info_box(ax, text_dict, x=0.03, y=-0.2):
    ax.text(
                x, y,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
                text_dict,
                transform=ax.transAxes,    # Coordinates relative to axes, not data values
                fontsize=9,
                fontfamily="monospace",    # Monospace keeps key-value pairs aligned
                verticalalignment="top",
                horizontalalignment="left",
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


def save_metadata():
    get_repo_version()

def plot_OSA_data():
    config_key = 'OSA_data'
    data = load_data(config_key)
    
    for index, row in data.iterrows():
        file_info = (
            f"Index: {row['exp_index']:03d}\n"
            f"QWP: {row['QWP']} deg\n"
            f"HWP1: {row['HWP1']} deg\n"
            f"HWP2: {row['HWP2']} deg\n"
            f"Pump current: {row['Pump current']} mA\n"
            f"Center Wavelength (nm): {row['Center Wavelength (nm)']:.2f} nm\n"
            f"FWHM Wavelength (nm): {row['FWHM Wavelength (nm)']:.2f} nm\n"
            f"Notes: {row['Notes']}\n"
        )
        fig, ax = plt.subplots()
        ax.plot(row["Wavelength (nm)"], row["Normalized Power (mW)"], label='Data')
        ax.plot(row['Wavelength (nm)'], gaussian(row['Wavelength (nm)'], 
                                                 1, 
                                                 row['Center Wavelength (nm)'],
                                                 FWHM_to_stddev(row['FWHM Wavelength (nm)']),
                                                 0),
                                                 color='black',
                                                 linestyle='--',
                                                 label='Gaussian Fit')
        
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Normalized Intensity (mW)")
        ax.grid(True)
        ax.legend()


        # 3. Define box styling
        

        # 4. Add text box (positioned at top-left inside axes)
        ax.text(
            1.03, 0.95,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
            file_info,
            transform=ax.transAxes,    # Coordinates relative to axes, not data values
            fontsize=9,
            fontfamily="monospace",    # Monospace keeps key-value pairs aligned
            verticalalignment="top",
            horizontalalignment="left",
            bbox=BBOX_PROPS
        )
        ax.set_title(f"OSA Data - {row['date']}")
        ax = add_info_box(ax, file_info)
        save_and_close_plot(config_key, row['source_file'])
        

def plot_RF_data():
    config_key = 'RF_data'
    data = load_data(config_key)
    print(f"Data has {len(data)} data lines.")
    for index, row in data.iterrows():
        file_info = (
                    f"Index: {row['exp_index']:03d}\n"
                    f"QWP: {row.get('QWP', 'NA')} deg\n"
                    f"HWP1: {row.get('HWP1', 'NA')} deg\n"
                    f"HWP2: {row.get('HWP2', 'NA')} deg\n"
                    f"Pump current: {row.get('Pump current', 'NA')} mA\n"
                    f"Notes: {row.get('Notes', 'NA')}\n"
                )
        fig, ax = plt.subplots()
        ax.plot(np.array(row['Frequency (Hz)']) * 1e-6, row['Power (dBm)'])

      


        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Power (dBm)')
        ax.set_title(f"RF Data - {row['date']}")
        ax.grid()
        
        ax = add_info_box(ax, file_info)
        save_and_close_plot(config_key, row['source_file'])
        
def plot_aurora_data():
    
    config_key = 'aurora_data'
    data = load_data(config_key)

    for index, row in data.iterrows():
        file_info = (
                    f"Device Name: {row.get('Device Name', 'NA')} mA\n"
                    f"Integral Time(s): {row['Integral Time(s)']:03d}\n"
                    f"Avg Count: {row.get('Avg Count', 'NA')} deg\n"
                    f"Center Wavelength (nm): {row.get('Center Wavelength (nm)', 'NA'):.2f} deg\n"
                    f"FWHM Wavelength (nm): {row.get('FWHM Wavelength (nm)', 'NA'):.2f} deg\n"
                    f"Other Description: {row.get('Other Description', 'NA')}\n"
                    )
        fig, ax = plt.subplots()
        ax.plot(np.array(row[f"Wavelength ({row['X-Axis Unit']})"]), np.array(row[f"Normalized Power (mW)"]))
        ax.plot(row['Wavelength (nm)'], gaussian(row['Wavelength (nm)'], 
                                                         1, 
                                                         row['Center Wavelength (nm)'],
                                                         FWHM_to_stddev(row['FWHM Wavelength (nm)']),
                                                         0),
                                                         color='black',
                                                         linestyle='--',
                                                         label='Gaussian Fit')
                


        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Normalized Power (mW)')
        ax.set_title(f"Aurora 4000 Data - {row['source_file']}")
        ax.grid()
        
        ax = add_info_box(ax, file_info)
        save_and_close_plot(config_key, row['source_file'])

def plot_ocean_optics_data():
    
    config_key = 'ocean_optics_data'
    data = load_data(config_key)

    for index, row in data.iterrows():
        file_info = (
                    f"Device Name: {row.get('Spectrometer', 'NA')} mA\n"
                    f"Integral Time(s): {row['Integration Time (sec)']}\n"
                    f"Scans to average: {row.get('Scans to average', 'NA')} deg\n"
                    f"Center Wavelength (nm): {row.get('Center Wavelength (nm)', 'NA')} deg\n"
                    f"FWHM Wavelength (nm): {row.get('FWHM Wavelength (nm)', 'NA')} deg\n"
                    f"Other Description: {row.get('Other Description', 'NA')}\n"
                    )
        fig, ax = plt.subplots()
        ax.plot(np.array(row[f"Wavelength (nm)"]), np.array(row[f"Normalized Power (mW)"]))
        ax.plot(row['Wavelength (nm)'], gaussian(row['Wavelength (nm)'], 
                                                1, 
                                                row['Center Wavelength (nm)'],
                                                FWHM_to_stddev(row['FWHM Wavelength (nm)']),
                                                0),
                                                color='black',
                                                linestyle='--',
                                                label='Gaussian Fit')
                
      
     
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Normalized Power (mW)')
        ax.set_title(f"Ocean Optics Data - {row['source_file']}")
        ax.grid()
        
        ax = add_info_box(ax, file_info)
        save_and_close_plot(config_key, row['source_file'])

def plot_FROG_data():
    
    config_key = 'FROG_data'
    data = load_data(config_key)
    for index, row in data.iterrows():
        file_info = (
                    f"Pulse Width: {row.get('pulse_width', 'NA')} {row.get('pulse_width_unit', 'NA')}\n"
                    f"Bandwidth: {row['bandwidth']} {row['bandwidth_unit']} \n"
                    f"Bandwidth (nm): {row['bandwidth_nm']} nm \n"
                    f"TBW product (g: 0.441, sec2: 0.315): {row.get('tbw_product', 'NA')}\n"
                    f"FROG trace error: {row.get('frog_trace_error', 'NA'):.3}\n"
                    f"Timestamp: {row.get('timestamp', 'NA')} deg\n"
                    f"Other Description: {row.get('Other Description', 'NA')}\n"
                    )
        
        fig, ax = plt.subplots(1, 3, figsize=(10, 4), dpi = 100)

        ax[0].plot(np.array(row["pulse_time_data_time"]), np.array(row["pulse_time_data_intensity"]))
        ax[0].set_xlabel('Time (fw)')
        ax[0].set_ylabel('Normalized Power (mW)')
        ax[0].set_title(f"Pulse temporal data \n{row['source_file']}")
        ax[0].grid()
        
        ax[1].plot(np.array(row["pulse_freq_data_frequency"]), np.array(row["pulse_freq_data_intensity"]))
        ax[1].set_xlabel('Wavelength (nm)')
        ax[1].set_ylabel('Normalized Power (mW)')
        ax[1].set_title(f" - Pulse spectral data")
        ax[1].grid()
    
        
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
    save_metadata()
    #create_all_graphs()
