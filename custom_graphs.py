
import tomllib
from pathlib import Path

import pandas as pd

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

DATA_FOLDER = Path(config['processed_data']['processed_data_folder'])

OSA_DATA = pd.read_json(DATA_FOLDER / config['OSA_data']['data_file'])
RF_DATA = pd.read_json(DATA_FOLDER / config['RF_data']['data_file'])
AURORA_DATA = pd.read_json(DATA_FOLDER / config['aurora_data']['data_file'])
OCEAN_OPTICS_DATA = pd.read_json(DATA_FOLDER / config['ocean_optics_data']['data_file'])


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