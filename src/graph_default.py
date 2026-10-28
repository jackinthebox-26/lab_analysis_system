from pathlib import Path
from datetime import datetime
import tomllib

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = Path(config['processed_data']['processed_data_folder'])

PROCESSED_DATA_PATH  = BASE_DIR / PROCESSED_DATA_PATH


def gaussian(x, amplitude, mean, stddev, offset):
    """1D Gaussian model with a baseline offset."""
    x = np.hstack(x).astype(float)
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset

def FWHM_to_stddev(FWHM):
    return 0.424661 * FWHM
def plot_OSA_data():
    file_path = PROCESSED_DATA_PATH / config['OSA_data']['data_file']
    if not file_path.is_file():
        return
    data = pd.read_json(file_path)
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
        bbox_props = dict(
            boxstyle="round,pad=0.5",  # Options: 'square', 'round', 'sawtooth'
            facecolor="wheat",         # Background fill color
            edgecolor="gray",          # Border line color
            alpha=0.8,                 # Transparency (0 to 1)
            linewidth=1.2
        )

        # 4. Add text box (positioned at top-left inside axes)
        ax.text(
            1.03, 0.95,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
            file_info,
            transform=ax.transAxes,    # Coordinates relative to axes, not data values
            fontsize=9,
            fontfamily="monospace",    # Monospace keeps key-value pairs aligned
            verticalalignment="top",
            horizontalalignment="left",
            bbox=bbox_props
        )
        ax.set_title(f"OSA Data - {row['date']}")

        plt.tight_layout()
        OSA_plots_path = Path(config['OSA_data']['plot_folder'])
        OSA_plots_path.mkdir(parents=True, exist_ok=True)
        plt.savefig(OSA_plots_path / f"plot_{row['source_file'][:-4]}.png")
        plt.close()

def plot_RF_data():
    print("Initializing RF data plot")
    file_path = PROCESSED_DATA_PATH / config['RF_data']['data_file']
    print(f"Loading {file_path}")
    if not file_path.is_file():
        return
    data = pd.read_json(file_path)
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

        
        # 3. Define box styling
        bbox_props = dict(
            boxstyle="round,pad=0.5",  # Options: 'square', 'round', 'sawtooth'
            facecolor="wheat",         # Background fill color
            edgecolor="gray",          # Border line color
            alpha=0.8,                 # Transparency (0 to 1)
            linewidth=1.2
        )

        # 4. Add text box (positioned at top-left inside axes)
        ax.text(
            0.03, -0.2,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
            file_info,
            transform=ax.transAxes,    # Coordinates relative to axes, not data values
            fontsize=9,
            fontfamily="monospace",    # Monospace keeps key-value pairs aligned
            verticalalignment="top",
            horizontalalignment="left",
            bbox=bbox_props
        )

        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Power (dBm)')
        ax.set_title(f"RF Data - {row['date']}")
        ax.grid()
        RF_plot_folder = Path(config['RF_data']['plot_folder'])
        
        RF_plot_folder.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(RF_plot_folder / f"plot_{row['source_file'][:-4]}.png")
        plt.close()
        
def plot_aurora_data():
    file_path = PROCESSED_DATA_PATH / config['aurora_data']['data_file']
    print(file_path)
    if not file_path.is_file():
        return
    data = pd.read_json(file_path)
    print(data)
    print(data.columns)

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
                


        # 3. Define box styling
        bbox_props = dict(
            boxstyle="round,pad=0.5",  # Options: 'square', 'round', 'sawtooth'
            facecolor="wheat",         # Background fill color
            edgecolor="gray",          # Border line color
            alpha=0.8,                 # Transparency (0 to 1)
            linewidth=1.2
        )
        
        # 4. Add text box (positioned at top-left inside axes)
        ax.text(
            0.03, -0.2,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
            file_info,
            transform=ax.transAxes,    # Coordinates relative to axes, not data values
            fontsize=9,
            fontfamily="monospace",    # Monospace keeps key-value pairs aligned
            verticalalignment="top",
            horizontalalignment="left",
            bbox=bbox_props
        )

        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Normalized Power (mW)')
        ax.set_title(f"Aurora 4000 Data - {row['source_file']}")
        ax.grid()
        plot_folder = Path(config['aurora_data']['plot_folder'])
        
        plot_folder.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(plot_folder / f"plot_{row['source_file'][:-4]}.png")

def plot_ocean_optics_data():
    file_path = PROCESSED_DATA_PATH / config['ocean_optics_data']['data_file']
    print(file_path)
    if not file_path.is_file():
        return
    data = pd.read_json(file_path)
    print(data)
    print(data.columns)

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
                
        
        # 3. Define box styling
        bbox_props = dict(
            boxstyle="round,pad=0.5",  # Options: 'square', 'round', 'sawtooth'
            facecolor="wheat",         # Background fill color
            edgecolor="gray",          # Border line color
            alpha=0.8,                 # Transparency (0 to 1)
            linewidth=1.2
        )
        
        # 4. Add text box (positioned at top-left inside axes)
        ax.text(
            0.03, -0.2,                # (x, y) coordinates in relative axes space (3% from left, 95% from bottom)
            file_info,
            transform=ax.transAxes,    # Coordinates relative to axes, not data values
            fontsize=9,
            fontfamily="monospace",    # Monospace keeps key-value pairs aligned
            verticalalignment="top",
            horizontalalignment="left",
            bbox=bbox_props
        )
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Normalized Power (mW)')
        ax.set_title(f"Ocean Optics Data - {row['source_file']}")
        ax.grid()
        plot_folder = Path(config['ocean_optics_data']['plot_folder'])
        
        plot_folder.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(plot_folder / f"plot_{row['source_file'][:-4]}.png")
    

def create_all_graphs():
    print("Initializing plot creation")
    print("Creating OSA graphs")
    plot_OSA_data()
    print("Creating RF analyser graphs")
    plot_RF_data()
    print("Creating Aurora 4000 graphs")
    plot_aurora_data()
    print("Creating Ocean Optics graphs")
    plot_ocean_optics_data()
    print("Completed graph creation")

    

if __name__ == "__main__":
    create_all_graphs()
