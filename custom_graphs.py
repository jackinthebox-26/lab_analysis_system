
import tomllib
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



BASE_DIR = Path(__file__).resolve().parent
config_path = BASE_DIR / 'config' / 'data_load_config.toml'

with open(config_path, 'rb') as f:
    config = tomllib.load(f)



RAW_DIR = Path(config['raw_data']['raw_data_folder'])
PROCESSED_DATA_PATH = Path(config['processed_data']['processed_data_folder'])
if config['processed_data']['store_processed_with_data']:
    PROCESSED_DATA_PATH = RAW_DIR / PROCESSED_DATA_PATH

FIGURE_PATH = Path(config['processed_data']['plot_data_folder'])

if config['processed_data']['store_plots_with_data']:
    FIGURE_PATH = RAW_DIR / FIGURE_PATH

PROCESSED_DATA_PATH  = BASE_DIR / PROCESSED_DATA_PATH

def load_all_data() -> dict[str, pd.DataFrame]:
    return {
        "osa": pd.read_json(PROCESSED_DATA_PATH / config['OSA_data']['data_file']),
        "rf": pd.read_json(PROCESSED_DATA_PATH / config['RF_data']['data_file']),
        "aurora": pd.read_json(PROCESSED_DATA_PATH / config['aurora_data']['data_file']),
        "ocean_optics": pd.read_json(PROCESSED_DATA_PATH / config['ocean_optics_data']['data_file']),
    }


def gaussian(x, amplitude, mean, stddev, offset):
    """1D Gaussian model with a baseline offset."""
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset

def FWHM_to_stddev(FWHM):
    return (1 / (2 * np.sqrt(2 * np.log(2)))) * FWHM

def inspect_data_files():
    data_dict = load_all_data()
    print('--OSA data--')
    print(data_dict['osa'].columns)
    print(data_dict['osa'].head())
    
    print('--RF data--')
    print(data_dict['rf'].columns)
    print(data_dict['rf'].head())

    
    print('--Aurora 4000 data--')
    print(data_dict['aurora'].columns)
    print(data_dict['aurora'].head())

    print('--Ocean Optics data--')
    print(data_dict['ocean_optics'].columns)
    print(data_dict['ocean_optics'].head())


def aurora_OO_comparison():
    data_dict = load_all_data()
    def plot_comparison(data_1, data_2):
        print(data_1.columns)
        print(data_2)

        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        ax[0].plot(np.hstack(data_1['Wavelength (nm)']), 
                    np.hstack(data_1['Normalized Power (mW)']),
                    label='Ocean Optics')

        

        ax[0].plot(np.hstack(data_2['Wavelength (nm)']), 
                         np.hstack(data_2['Normalized Power (mW)']),
                         '.--',
                         label='Aurora')

        delta_wavelength = float(data_1['Center Wavelength (nm)'].item()) -  float(data_2['Center Wavelength (nm)'].item())
        
        ax[1].plot(np.hstack(data_1['Wavelength (nm)']), 
                            np.hstack(data_1['Normalized Power (mW)']),
                            label='Ocean Optics')
        
                
        
        ax[1].plot(np.hstack(data_2['Wavelength (nm)']) + delta_wavelength, 
                            np.hstack(data_2['Normalized Power (mW)']),
                            '.--',
                            label=f'Aurora - {delta_wavelength:.2f} nm shift')

        print(data_1['Center Wavelength (nm)'])
        center_wavelength = float(data_1['Center Wavelength (nm)'].item())
        fwhm_wavelength = float(data_1['FWHM Wavelength (nm)'].item())

        scale = 4

        ax[0].set_xlim([center_wavelength  + scale *  fwhm_wavelength,
                    center_wavelength  - scale *  fwhm_wavelength]) # type: ignore
        ax[1].set_xlim([center_wavelength  + scale *  fwhm_wavelength,
                    center_wavelength  - scale *  fwhm_wavelength]) # type: ignore
        ax[0].grid()
        ax[1].grid()
        ax[0].legend()
        ax[1].legend()

        ax[0].set_xlabel('Wavelength (nm)')
        ax[0].set_ylabel('Normalized Power (mW)')
        ax[1].set_xlabel('Wavelength (nm)')
        ax[1].set_ylabel('Normalized Power (mW)')

        ax[0].set_title(f"Comparison of Ocean Optics and Aurora Spectra\nCenter Wavelength: {center_wavelength:.2f} nm, FWHM: {fwhm_wavelength:.2f} nm")
        ax[1].set_title(f"Comparison of Ocean Optics and Aurora Spectra\nCenter Wavelength: {center_wavelength:.2f} nm, FWHM: {fwhm_wavelength:.2f} nm")
        plt.show()

    ocean_optics = data_dict['ocean_optics']
    aurora = data_dict['aurora']

    data_1017_nm_ocean = ocean_optics[ocean_optics['source_file'] == 
                                      'FHG_full_power_nov03_2026_HR6009442__2__15-14-00-161.txt']

    data_1017_nm_aurora = aurora[aurora['source_file'] == 'FHG_full_power_nov03.txt']

    data_1016_nm_ocean = ocean_optics[ocean_optics['source_file'] == 
                                          'FHG_1016_tuning_nov3_2026_HR6009441__0__19-04-53-747.txt']
    
    data_1016_nm_aurora = aurora[aurora['source_file'] == 'FHG_full_power_OSC_1016nm_nov03.txt']
    
    print(data_dict)
    plot_comparison(data_1017_nm_ocean, 
                    data_1017_nm_aurora)
    plot_comparison(data_1016_nm_ocean, 
                    data_1016_nm_aurora)

def main():
    
    #inspect_data_files()
    aurora_OO_comparison()
if __name__ == "__main__":
    main()