from pathlib import Path
import shutil

import tomllib

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

raw_data = Path(config['raw_data']['raw_data_folder'])
project_root = Path(__file__).parent.parent

processed_data_folder = config['processed_data']['processed_data_folder']
if config['processed_data']['store_processed_with_data'].strip().lower() == "true":
    processed_data_folder = raw_data / processed_data_folder
processed_data_folder = project_root / processed_data_folder
plot_data_folder = project_root / config['processed_data']['plot_data_folder']
if config['processed_data']['store_plots_with_data'].strip().lower() == "true":
    plot_data_folder = raw_data / plot_data_folder
plot_data_folder = project_root / plot_data_folder

folder_list = [processed_data_folder, plot_data_folder]
PROTECTED_EXTENSIONS = [".py", ".toml", ".md", ".txt", ".gitkeep", ".gitignore"]

def clean_folder(folder_path):
    deleted_count = 0
    if not folder_path.exists():
        print(f"Directory does not exist yet: {folder_path}")
        return 0
    for item in folder_path.iterdir():
        if item.suffix not in PROTECTED_EXTENSIONS:
            if item.is_dir():
                shutil.rmtree(item)
                print(f"Deleted {item.name}")
                deleted_count += 1
            if item.is_file():
                item.unlink()
                print(f"Deleted {item.name}")
                deleted_count += 1
    return deleted_count



def clean_directories():
    print("-------------------Initializing tree cleaning-------------------")
    deleted_count = 0
    for folder in folder_list:
        deleted_count += clean_folder(folder)
    print(f"Deleted {deleted_count} files from {len(folder_list)} folders")
    

def main():
    clean_directories()
if __name__ == "__main__":
    main()