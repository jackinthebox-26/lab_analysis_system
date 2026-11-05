
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
        ax[0].plot(np.array(data_1['Wavelength (nm)'].item()), 
                    np.array(data_1['Normalized Power (mW)'].item()),
                    label='Ocean Optics')

        

        ax[0].plot(np.array(data_2['Wavelength (nm)'].item()), 
                         np.array(data_2['Normalized Power (mW)'].item()),
                         '.--',
                         label='Aurora')

        delta_wavelength = float(data_1['Center Wavelength (nm)'].item()) -  float(data_2['Center Wavelength (nm)'].item())
        
        ax[1].plot(np.array(data_1['Wavelength (nm)'].item()), 
                            np.array(data_1['Normalized Power (mW)'].item()),
                            label='Ocean Optics')
        
                
        
        ax[1].plot(np.array(data_2['Wavelength (nm)'].item()) + delta_wavelength, 
                            np.array(data_2['Normalized Power (mW)'].item()),
                            '.--',
                            label=f'Aurora - {delta_wavelength:.2f} nm shift')

        print(data_1['Center Wavelength (nm)'])
        center_wavelength = float(data_1['Center Wavelength (nm)'].item())
        fwhm_wavelength = float(data_1['FWHM Wavelength (nm)'].item())

        scale = 4

        ax[0].set_xlim([center_wavelength  - scale *  fwhm_wavelength,
                    center_wavelength  + scale *  fwhm_wavelength]) # type: ignore
        ax[1].set_xlim([center_wavelength  - scale *  fwhm_wavelength,
                    center_wavelength  + scale *  fwhm_wavelength]) # type: ignore
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
        plt.savefig(FIGURE_PATH / f"comparison_{center_wavelength:.2f}nm.png")

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

def aurora_angle_comparison():
    data_dict = load_all_data()
    aurora_data = data_dict['aurora']

    print(aurora_data['source_file'].unique())
    normal_incidence_data = aurora_data[aurora_data['source_file'] == 'FHG_full_power_OSC_1016nm_normal_incidence_nov03.txt']

    angle_1_data = aurora_data[aurora_data['source_file'] == 'FHG_full_power_OSC_1016nm_angle1_nov03.txt']
    angle_2_data = aurora_data[aurora_data['source_file'] == 'FHG_full_power_OSC_1016nm_angle2_nov03.txt']

    angle_3_data = aurora_data[aurora_data['source_file'] == 'FHG_full_power_OSC_1016nm_angle3_nov03.txt']
    angle_4_data = aurora_data[aurora_data['source_file'] == 'FHG_full_power_OSC_1016nm_angle4_nov03.txt']
    angle_list = ['Angle 4', 'Angle 3', 'Normal Incidence', 'Angle 2', 'Angle 1']
    center_wavelength_list = [angle_4_data['Center Wavelength (nm)'].item(),
                              angle_3_data['Center Wavelength (nm)'].item(),
                              normal_incidence_data['Center Wavelength (nm)'].item(),
                              angle_2_data['Center Wavelength (nm)'].item(),
                              angle_1_data['Center Wavelength (nm)'].item()]


    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    ax.plot(np.array(normal_incidence_data['Wavelength (nm)'].item()),
            np.array(normal_incidence_data['Normalized Power (mW)'].item()),
            label='Normal Incidence')

    ax.plot(np.array(angle_1_data['Wavelength (nm)'].item()),
            np.array(angle_1_data['Normalized Power (mW)'].item()),
            label='Angle 1')

    ax.plot(np.array(angle_2_data['Wavelength (nm)'].item()),
            np.array(angle_2_data['Normalized Power (mW)'].item()),
            label='Angle 2')

    ax.plot(np.array(angle_3_data['Wavelength (nm)'].item()),
            np.array(angle_3_data['Normalized Power (mW)'].item()),
            label='Angle 3')

    ax.plot(np.array(angle_4_data['Wavelength (nm)'].item()),
            np.array(angle_4_data['Normalized Power (mW)'].item()),
            label='Angle 4')

    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Normalized Power (mW)')

    ax.set_xlim(230, 300)
    ax.legend()
    ax.grid(which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(FIGURE_PATH / "aurora_angle_comparison.png")

    fig, ax = plt.subplots(1, 1, figsize=(6, 3))
    ax.plot(angle_list, center_wavelength_list, marker='o')
    ax.grid()
    ax.set_xlabel('Angle')
    ax.set_ylabel('Center Wavelength (nm)')
    plt.tight_layout()
    plt.savefig(FIGURE_PATH / "aurora_angle_center_wavelength.png")

def UV_generation_track():
    data_dict = load_all_data()
    def plot_UV_generation(data_OSC, data_AMP, data_UV, id):
        fig, ax = plt.subplots(1, 2, figsize=(12, 4))

        ax[0].plot(np.array(data_UV['Wavelength (nm)'].item()),
                np.array(data_UV['Normalized Power (mW)'].item()),
                label=f'UV  \n{data_UV["Center Wavelength (nm)"].item():.2f} nm \nFWHM: {data_UV["FWHM Wavelength (nm)"].item():.2f} nm')

        ax[0].plot(np.array(data_AMP['Wavelength (nm)'].item()) / 4,
                        np.array(data_AMP['Normalized Power (mW)'].item()),
                        label=f'AMP with wavelength/4\n {data_AMP["Center Wavelength (nm)"].item()/4:.2f} nm \nFWHM: {data_AMP["FWHM Wavelength (nm)"].item()/4:.2f} nm')

        ax[0].legend()
        ax[0].grid()
        ax[0].set_xlabel('Wavelength (nm)')
        ax[0].set_ylabel('Normalized Power (mW)')
        ax[0].set_xlim([250, 270])


        ax[1].plot(np.array(data_OSC['Wavelength (nm)'].item()),
                    np.array(data_OSC['Normalized Power (mW)'].item()),
                        label=f'OSC\n{data_OSC["Center Wavelength (nm)"].item():.2f} nm \nFWHM: {data_OSC["FWHM Wavelength (nm)"].item():.2f} nm')
        
        ax[1].plot(np.array(data_AMP['Wavelength (nm)'].item()),
                np.array(data_AMP['Normalized Power (mW)'].item()),
                label=f'AMP\n{data_AMP["Center Wavelength (nm)"].item():.2f} nm \nFWHM: {data_AMP["FWHM Wavelength (nm)"].item():.2f} nm')


        ax[1].legend()
        ax[1].grid()
        ax[1].set_xlabel('Wavelength (nm)')
        ax[1].set_ylabel('Normalized Power (mW)')
        plt.suptitle(f"UV Generation Track {id.capitalize()}")
        plt.savefig(FIGURE_PATH / f"UV_generation_track_{id}.png")
    OSA_data = data_dict['osa']
    ocean_optics_data = data_dict['ocean_optics']
    first_OSC_data = OSA_data[OSA_data['source_file'] == '017_HWP2_280_HWP1_135_QWP_256_580mA_OSC_20261103_143511.csv']
    first_AMP_data = OSA_data[OSA_data['source_file'] == '016_HWP2_280_HWP1_135_QWP_256_580mA_AMP_20261103_143423.csv']
    first_UV_data = ocean_optics_data[ocean_optics_data['source_file'] == 'FHG_full_power_nov03_2026_HR6009442__2__15-14-00-161.txt']
    plot_UV_generation(first_OSC_data, first_AMP_data, first_UV_data, 'first')

    second_OSC_data = OSA_data[OSA_data['source_file'] == '020_HWP2_282_HWP1_135_QWP_256_580mA_OSC_20261103_183110.csv']
    second_AMP_data = OSA_data[OSA_data['source_file'] == '021_HWP2_282_HWP1_135_QWP_256_580mA_AMP_20261103_183443.csv']
    second_UV_data = ocean_optics_data[ocean_optics_data['source_file'] == 'FHG_1016_tuning_nov3_2026_HR6009441__0__19-04-53-747.txt']
    plot_UV_generation(second_OSC_data, second_AMP_data, second_UV_data, 'second')

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    print(first_UV_data['Wavelength (nm)'].item())
    ax.plot(np.array(first_UV_data['Wavelength (nm)'].item()),
            np.array(first_UV_data['Normalized Power (mW)'].item()),
            label=f'UV with OSC: 1017 nm \n{first_UV_data["Center Wavelength (nm)"].item():.2f} nm \nFWHM: {first_UV_data["FWHM Wavelength (nm)"].item():.2f} nm')
    ax.plot(np.array(second_UV_data['Wavelength (nm)'].item()),
            np.array(second_UV_data['Normalized Power (mW)'].item()),
            label=f'UV with OSC: 1016 nm \n{second_UV_data["Center Wavelength (nm)"].item():.2f} nm \nFWHM: {second_UV_data["FWHM Wavelength (nm)"].item():.2f} nm')
    
    ax.vlines(x=256, ymin=0, ymax=1, colors='r', linestyles='--', label='Target Wavelength: 256 nm')
    ax.legend()
    ax.grid()
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Normalized Power (mW)')
    ax.set_xlim(250, 260)
    plt.savefig(FIGURE_PATH / "UV_generation_track_comparison.png")


def main():
    
    inspect_data_files()
    aurora_OO_comparison()
    aurora_angle_comparison()
    UV_generation_track()
if __name__ == "__main__":
    main()