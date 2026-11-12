
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

def main():
    
    inspect_data_files()


if __name__ == "__main__":
    main()