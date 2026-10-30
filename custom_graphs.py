
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
    return 0.424661 * FWHM

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



def main():
    inspect_data_files()
    
if __name__ == "__main__":
    main()