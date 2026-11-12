from pathlib import Path
import sys
import tomllib


BASE_DIR = Path(__file__).resolve().parent.parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


MPL_STYLE_PATH = BASE_DIR / 'config' / 'plot_style.mplstyle'


config_path = BASE_DIR / 'config' / 'data_load_config.toml'
config_path = Path(config_path)
with open(config_path, 'rb') as f:
    DATA_LOAD_CONFIG = tomllib.load(f)


fig_config_path = BASE_DIR / 'config' / 'figure_config.toml'
fig_config_path = Path(fig_config_path)
with open(fig_config_path, 'rb') as f:
    FIG_CONFIG = tomllib.load(f)



RAW_DIR = BASE_DIR / Path(DATA_LOAD_CONFIG['raw_data']['raw_data_folder'].lstrip('/\\'))
PROCESSED_TEMP_DATA_PATH = Path(DATA_LOAD_CONFIG['processed_data']['processed_data_folder'].lstrip('/\\'))
FIGURE_TEMP_PATH = Path(DATA_LOAD_CONFIG['processed_data']['plot_data_folder'].lstrip('/\\'))


if DATA_LOAD_CONFIG['processed_data']['store_processed_with_data']:
    PROCESSED_DATA_PATH =  RAW_DIR / PROCESSED_TEMP_DATA_PATH
else:
    PROCESSED_DATA_PATH = BASE_DIR / PROCESSED_TEMP_DATA_PATH
     


if DATA_LOAD_CONFIG['processed_data']['store_plots_with_data']:
    FIGURE_PATH = RAW_DIR / FIGURE_TEMP_PATH
else:
    FIGURE_PATH = BASE_DIR / FIGURE_TEMP_PATH

