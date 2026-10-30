
import tomllib
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)



BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = Path(config['raw_data']['raw_data_folder'])
PROCESSED_DATA_PATH = Path(config['processed_data']['processed_data_folder'])
if config['processed_data']['store_processed_with_data']:
    PROCESSED_DATA_PATH = RAW_DIR / PROCESSED_DATA_PATH

FIGURE_PATH = Path(config['processed_data']['plot_data_folder'])

if config['processed_data']['store_plots_with_data']:
    FIGURE_PATH = RAW_DIR / FIGURE_PATH

PROCESSED_DATA_PATH  = BASE_DIR / PROCESSED_DATA_PATH

OSA_DATA = pd.read_json(PROCESSED_DATA_PATH / config['OSA_data']['data_file'])
RF_DATA = pd.read_json(PROCESSED_DATA_PATH / config['RF_data']['data_file'])
AURORA_DATA = pd.read_json(PROCESSED_DATA_PATH / config['aurora_data']['data_file'])
OCEAN_OPTICS_DATA = pd.read_json(PROCESSED_DATA_PATH / config['ocean_optics_data']['data_file'])

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



def main():
    inspect_data_files()
    
if __name__ == "__main__":
    main()