
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



