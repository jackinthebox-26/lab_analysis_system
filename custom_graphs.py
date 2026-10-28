
import tomllib
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

DATA_FOLDER = Path(config['processed_data']['processed_data_folder'])

OSA_DATA = pd.read_json(DATA_FOLDER / config['OSA_data']['data_file'])
RF_DATA = pd.read_json(DATA_FOLDER / config['RF_data']['data_file'])
AURORA_DATA = pd.read_json(DATA_FOLDER / config['aurora_data']['data_file'])
OCEAN_OPTICS_DATA = pd.read_json(DATA_FOLDER / config['ocean_optics_data']['data_file'])

def gaussian(x, amplitude, mean, stddev, offset):
    """1D Gaussian model with a baseline offset."""
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset
def FWHM_to_stddev(FWHM):
    return 0.424661 * FWHM

def get_angle_number(series):
    filename = series['source_file']
    print(filename)
    pattern = r"__(\d+)__(\d+)\.\w+$"
    match = re.search(pattern, filename)

    if match:
        first_num = int(match.group(1))   # 0
        second_num = int(match.group(2))  # 0 (or "00000" as str via match.group(2))
        
        return second_num
    return None

def inspect_data_files():
    print('--OSA data--')
    print(OSA_DATA.columns)
    print(OSA_DATA.head())
    
    print('--RF data--')
    print(RF_DATA.columns)
    print(RF_DATA.head())

    
    print('--Aurora 4000 data--')
    print(AURORA_DATA.columns)
    print(AURORA_DATA.head())

    print('--Ocean Optics data--')
    print(OCEAN_OPTICS_DATA.columns)
    print(OCEAN_OPTICS_DATA.head())

def UV_generation_plot():

    x_label = 'Wavelength (nm)'
    y_label = 'Normalized Power (mW)'

    OSC_data = OSA_DATA[OSA_DATA['exp_index'] == 2]
    AMP_data = OSA_DATA[OSA_DATA['exp_index'] == 4]
    SHG_data = AURORA_DATA[AURORA_DATA['source_file'] == 'SHG_oct27_512nm_4dot07watt.txt']
    FHG_data = OCEAN_OPTICS_DATA[OCEAN_OPTICS_DATA['source_file'] == '2026-10-27-UV scan_low_power.txt']


    fig, ax = plt.subplots(figsize=(7,3))
    ax.plot(np.hstack(OSC_data[x_label]).astype(float), 
            np.hstack(OSC_data[y_label]).astype(float),
            label=f"OSC Center: {OSC_data['Center Wavelength (nm)'].iloc[0]:.2f} nm \nFWHM:  {OSC_data['FWHM Wavelength (nm)'].iloc[0]:.2f} nm\nPower = 20mW")
    print(OSC_data)
    print(AMP_data)
    ax.plot(np.hstack(AMP_data[x_label]).astype(float), 
            np.hstack(AMP_data[y_label]).astype(float),
            label=f"AMP Center: {AMP_data['Center Wavelength (nm)'].iloc[0]:.2f} nm\nFWHM:  {AMP_data['FWHM Wavelength (nm)'].iloc[0]:.2f} nm\nPower = 7.27 W")

    ax.plot(np.hstack(SHG_data[x_label]).astype(float), 
            np.hstack(SHG_data[y_label]).astype(float),
            label=f"SHG Center: {SHG_data['Center Wavelength (nm)'].iloc[0]:.2f} nm\nFWHM:  {SHG_data['FWHM Wavelength (nm)'].iloc[0]:.2f} nm\nPower = 4.07 W")

    ax.plot(np.hstack(FHG_data[x_label]).astype(float), 
            np.hstack(FHG_data[y_label]).astype(float),
            label=f"FHG Center: {FHG_data['Center Wavelength (nm)'].iloc[0]:.2f} nm\nFWHM:  {FHG_data['FWHM Wavelength (nm)'].iloc[0]:.2f} nm\n Power = 430 mW")

    ax.legend(loc="lower center", 
                bbox_to_anchor=(0.5, 1.02), 
                ncol=2,            # Number of columns (arranges items horizontally)
                frameon=True)       # Keep or remove border frame (True/False))
    ax.grid()

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    plt.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7,3))
    ax.plot(np.hstack(FHG_data[x_label]).astype(float), 
                np.hstack(FHG_data[y_label]).astype(float),
                label=f"FHG Center: {FHG_data['Center Wavelength (nm)'].iloc[0]:.2f} nm\nFWHM:  {FHG_data['FWHM Wavelength (nm)'].iloc[0]:.2f} nm\n Power = 430 mW")
    ax.plot(np.hstack(FHG_data[x_label]).astype(float),
            gaussian(np.hstack(FHG_data[x_label]), 
                     1, 
                     float(FHG_data['Center Wavelength (nm)'].iloc[0]), 
                     float(FWHM_to_stddev(FHG_data['FWHM Wavelength (nm)'].iloc[0])), 
                     0),
                     '--',
                     label='Gaussian fit')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim([255, 257])

    ax.grid()
    ax.legend()
    plt.tight_layout()
    plt.show()

def angle_analysis():
    angle_power_data = pd.read_csv(Path(config['raw_data']['raw_data_folder']) / 'angle_power_data.csv')
    angle_power_data = angle_power_data.sort_values(by='Crystal angle')
    print(angle_power_data.columns)
    OCEAN_OPTICS_DATA['angle_ID'] = OCEAN_OPTICS_DATA.apply(get_angle_number, axis=1)
    fig, ax = plt.subplots()
    for idx, row in angle_power_data.iterrows():
        print(row['Spectra ID'])
        temp_df = OCEAN_OPTICS_DATA[OCEAN_OPTICS_DATA['angle_ID'] == row['Spectra ID']]
        print(temp_df)
        ax.plot(np.hstack(temp_df['Wavelength (nm)']).astype(float), 
                row['Location 3 power mW'] * np.hstack(temp_df['Normalized Power (mW)']).astype(float),
                label=f"Micrometer: {row['Crystal angle']} deg")

    ax.legend()
    ax.set_xlim([255, 257])
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Power (mW)')
    ax.grid()
    plt.show()


    fig, ax = plt.subplots(figsize=(3,3))
    ax.plot(angle_power_data['Crystal angle'], angle_power_data['Location 3 power mW'], '-o')
    ax.set_xlabel('Crystal angle')
    ax.set_ylabel('Power (mW)')
    ax.grid()
    plt.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(3,3))
    temp_array = []
    for idx, row in angle_power_data.iterrows():
            print(row['Spectra ID'])
            temp_df = OCEAN_OPTICS_DATA[OCEAN_OPTICS_DATA['angle_ID'] == row['Spectra ID']]
            temp_array.append(temp_df['Center Wavelength (nm)'])
    ax.plot(angle_power_data['Crystal angle'], temp_array, '-o')
    ax.set_xlabel('Crystal angle')
    ax.set_ylabel('Center Wavelength (nm)')
    ax.grid()
    plt.tight_layout()
    plt.show()

def UV_layout_power_study():
    data = pd.read_csv(Path(config['raw_data']['raw_data_folder']) / 'UV_layout_power_study.csv')
    print(data.columns)

    fig, ax = plt.subplots()
    ax.plot(np.hstack(data['HWP angle']).astype(float), 
            np.hstack(data['Location 1 power mW']).astype(float),
            '-o',
            label='Loc 1')
    
    ax.plot(np.hstack(data['HWP angle']).astype(float), 
            np.hstack(data['Location 2 power mW']).astype(float),
            '-o',
            label='Loc 2')
    
    ax.plot(np.hstack(data['HWP angle']).astype(float), 
            np.hstack(data['Location 3 power mW']).astype(float),
            '-o',
            label='Loc 3')


    ax.set_xlabel('HWP angle (deg)')
    ax.set_ylabel('Power (mW)')

    ax.grid()
    ax.legend()
    plt.show()
    


def main():
    #inspect_data_files()
    UV_generation_plot()
    #angle_analysis()
    #UV_layout_power_study()

if __name__ == "__main__":
    main()