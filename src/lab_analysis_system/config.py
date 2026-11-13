from pathlib import Path
import logging
import matplotlib.pyplot as plt
import tomllib


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


MPL_STYLE_PATH = BASE_DIR / "config" / "plot_style.mplstyle"
if MPL_STYLE_PATH.is_file():
    plt.style.use(MPL_STYLE_PATH)


config_path = BASE_DIR / 'config' / 'data_load_config.toml'
config_path = Path(config_path)
with open(config_path, 'rb') as f:
    DATA_LOAD_CONFIG = tomllib.load(f)


fig_config_path = BASE_DIR / 'config' / 'figure_config.toml'
fig_config_path = Path(fig_config_path)
with open(fig_config_path, 'rb') as f:
    FIG_CONFIG = tomllib.load(f)
def resolve_paths(raw_folder: str | Path | None = None) -> tuple[Path, Path, Path]:
    folder = Path(raw_folder or DATA_LOAD_CONFIG['raw_data']['raw_data_folder'])
    raw_dir = folder.resolve() if folder.is_absolute() else (BASE_DIR / folder).resolve()
    
    proc_rel = Path(DATA_LOAD_CONFIG['processed_data']['processed_data_folder'].lstrip('/\\'))
    fig_rel = Path(DATA_LOAD_CONFIG['processed_data']['plot_data_folder'].lstrip('/\\'))

    proc_path = (raw_dir / proc_rel) if DATA_LOAD_CONFIG['processed_data']['store_processed_with_data'] else (BASE_DIR / proc_rel)
    fig_path = (raw_dir / fig_rel) if DATA_LOAD_CONFIG['processed_data']['store_plots_with_data'] else (BASE_DIR / fig_rel)
    return raw_dir, proc_path, fig_path


RAW_DIR, PROCESSED_DATA_PATH, FIGURE_PATH = resolve_paths()


