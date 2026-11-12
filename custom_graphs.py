
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from package.config import DATA_LOAD_CONFIG, FIG_CONFIG, PROCESSED_DATA_PATH, FIGURE_PATH
from package.math_tools import gaussian, FWHM_to_stddev

def load_all_data() -> dict[str, pd.DataFrame]:
    data_sources = {
        "osa": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['OSA_data']['data_file'],
        "rf": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['RF_data']['data_file'],
        "aurora": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['aurora_data']['data_file'],
        "ocean_optics": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['ocean_optics_data']['data_file'],
    }
    
    loaded_data: dict[str, pd.DataFrame] = {}
    
    for key, path in data_sources.items():
        path = Path(path)
        if path.exists():
            temp_df = pd.read_json(path)
            for col in temp_df.columns:
                if isinstance(temp_df[col].iloc[0], list):
                    temp_df[col] = temp_df[col].apply(np.array)
            loaded_data[key] = temp_df
        else:
            print(f"Warning: Data file for {key} not found at {path}.")
            
    return loaded_data


def inspect_data_files():
    data_dict = load_all_data()

    if 'osa' in data_dict:
        print('--OSA data--')
        print(data_dict['osa'].columns)
        print(data_dict['osa'].info())
    else:
        print("No OSA data found.")
    
    if 'rf' in data_dict:
        print('--RF data--')
        print(data_dict['rf'].columns)
        print(data_dict['rf'].info())
    else:
        print("No RF data found.")

    if 'aurora' in data_dict:
        print('--Aurora 4000 data--')
        print(data_dict['aurora'].columns)
        print(data_dict['aurora'].info())
    else:
        print("No Aurora 4000 data found.")

    if 'ocean_optics' in data_dict:
        print('--Ocean Optics data--')
        print(data_dict['ocean_optics'].columns)
        print(data_dict['ocean_optics'].info())
    else:
        print("No Ocean Optics data found.")


def plot_UV_spectra():
    data_dict = load_all_data()
    ocean_optics_data = data_dict.get('ocean_optics')

    if ocean_optics_data is None:
        print("No Ocean Optics data found. Cannot plot UV spectra.")
        return

    this_data = ocean_optics_data[ocean_optics_data['source_file'] == 'FHG_1016_tuning_nov3_2026_HR6009441__0__19-04-53-747.txt']
    
    fig, ax = plt.subplots(figsize=FIG_CONFIG['default_fig_settings']['figsize'], dpi=FIG_CONFIG['default_fig_settings']['dpi'])
    ax.plot(this_data['Wavelength (nm)'].values[0], this_data['Normalized Power (mW)'].values[0], color='purple', label=f'Data: $P$ = 340 mW')

    gaussian_fit = gaussian(this_data['Wavelength (nm)'].values[0],1, this_data['Center Wavelength (nm)'].values[0], FWHM_to_stddev(this_data['FWHM Wavelength (nm)'].values[0]), 0)
    ax.plot(this_data['Wavelength (nm)'].values[0], gaussian_fit, color='black', alpha=0.5, linestyle='--', label=r'Fit: $\lambda_0$ = {:.2f} nm, FWHM = {:.2f} nm'.format(this_data['Center Wavelength (nm)'].values[0], this_data['FWHM Wavelength (nm)'].values[0]))
    ax.vlines(256, ymin=0, ymax=1, color='k', linestyle=':', label='256 nm')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Normalized Power (mW)')
    ax.set_title('UV Spectrum')
    ax.set_xlim(254, 258)
    ax.legend()
    ax.grid()
    plt.savefig(FIGURE_PATH / '256_brag.png', dpi=FIG_CONFIG['default_fig_settings']['dpi'])
    plt.close(fig)

def plot_IR_spectra():
    data_dict = load_all_data()
    osa_data = data_dict.get('osa')
    if osa_data is None:
        print("No OSA data found. Cannot plot IR spectra.")
        return
    this_data = osa_data[osa_data['exp_index'] == 20]
    this_amp_data = osa_data[osa_data['exp_index'] == 21]
   
    fig, ax = plt.subplots(figsize=(15, 4), dpi=FIG_CONFIG['default_fig_settings']['dpi'])
    ax.plot(this_data['Wavelength (nm)'].values[0], this_data['Normalized Power (mW)'].values[0], color='orangered', label=f'OSA Data: $P$ = 20 mW')
    ax.plot(this_amp_data['Wavelength (nm)'].values[0], this_amp_data['Normalized Power (mW)'].values[0], color='red', label=f'AMP Data: $P$ = 7.1 W')

    gaussian_fit = gaussian(this_data['Wavelength (nm)'].values[0],1, this_data['Center Wavelength (nm)'].values[0], FWHM_to_stddev(this_data['FWHM Wavelength (nm)'].values[0]), 0)
    ax.plot(this_data['Wavelength (nm)'].values[0], gaussian_fit, color='black', alpha=0.5, linestyle='--', label=r'Fit: $\lambda_0$ = {:.2f} nm, FWHM = {:.2f} nm'.format(this_data['Center Wavelength (nm)'].values[0], this_data['FWHM Wavelength (nm)'].values[0]))
    gaussian_fit = gaussian(this_amp_data['Wavelength (nm)'].values[0],1, this_amp_data['Center Wavelength (nm)'].values[0], FWHM_to_stddev(this_amp_data['FWHM Wavelength (nm)'].values[0]), 0)
    ax.plot(this_amp_data['Wavelength (nm)'].values[0], gaussian_fit, color='black', alpha=0.5, linestyle='--', label=r'Fit: $\lambda_0$ = {:.2f} nm, FWHM = {:.2f} nm'.format(this_amp_data['Center Wavelength (nm)'].values[0], this_amp_data['FWHM Wavelength (nm)'].values[0]))
        
    
    ax.vlines(1016, ymin=0, ymax=1, color='k', linestyle=':', label='1016 nm')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Normalized Power (mW)')
    ax.set_title('OSC and Amplifier Spectra')
    ax.set_xlim(1000, 1040)
    plt.legend(loc="center right", bbox_to_anchor=(-0.1, 0.5))
    ax.grid()
    plt.tight_layout()
    plt.savefig(FIGURE_PATH / '1016_brag.png', dpi=FIG_CONFIG['default_fig_settings']['dpi'])
    plt.close(fig)

def main():
    
    #inspect_data_files()
    plot_UV_spectra()
    plot_IR_spectra()


if __name__ == "__main__":
    main()