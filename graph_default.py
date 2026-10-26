from pathlib import Path
from datetime import datetime
import tomllib

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

PROCESSED_DATA_PATH = Path(config['processed_data']['processed_data_folder'])

def plot_OSA_data():
    file_path = PROCESSED_DATA_PATH / "OSA_data.json"
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
            f"Notes: {row['Notes']}\n"
        )
        fig, ax = plt.subplots()
        ax.plot(row["Wavelength (nm)"], row["Power (mW)"])
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Intensity (mW)")
        ax.grid(True)

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
        OSA_plots_path = Path('processed_data/OSA_plots')
        OSA_plots_path.mkdir(parents=True, exist_ok=True)
        plt.savefig(OSA_plots_path / f"plot_{row['source_file'][:-4]}.png")
        plt.close()

def plot_RF_data():
    file_path = PROCESSED_DATA_PATH / "RF_data.json"
    if not file_path.is_file():
        return
    data = pd.read_json(file_path)
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

        plt.tight_layout()
        plt.savefig(f"processed_data/RF_plots/plot_{row['source_file'][:-4]}.png")
        plt.close()
        
def plot_aurora_data():
    file_path = PROCESSED_DATA_PATH / "aurora_data.json"
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
                    f"Smoothness: {row.get('Smoothness', 'NA')} deg\n"
                    f"Data Type: {row.get('Data Type', 'NA')} deg\n"
                    f"Other Description: {row.get('Other Description', 'NA')}\n"
                    )
        fig, ax = plt.subplots()
        ax.plot(np.array(row[f"Wavelength ({row['X-Axis Unit']})"]), np.array(row[f"Power ({row['Y-Axis Unit']})"]))

            
        plt.savefig(f"processed_data/aurora_plots/plot_{row['source_file'][:-4]}.png")
    


    

if __name__ == "__main__":
    plot_OSA_data()
    plot_RF_data()
    plot_aurora_data()
