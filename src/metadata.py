from datetime import datetime
import tomllib
from pathlib import Path


import git


config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = Path(config['raw_data']['raw_data_folder'])
RAW_DATA_DIR = BASE_DIR / RAW_DATA_DIR
PROCESSED_DIR = Path(config['processed_data']['processed_data_folder'])
if config['processed_data']['store_processed_with_data']:
    PROCESSED_DIR = RAW_DATA_DIR / PROCESSED_DIR

PROCESSED_DIR = BASE_DIR / PROCESSED_DIR
PLOT_DIR = Path(config['processed_data']['plot_data_folder'])
if config['processed_data']['store_plots_with_data']:
    PLOT_DIR = RAW_DATA_DIR / PLOT_DIR

PLOT_DIR = BASE_DIR / PLOT_DIR

def find_all_files(data_dir): # Called in LabDataLoader.make_raw_data_dict()
        # Implement the logic to find all files in the specified directory
        all_files = [f.resolve() for f in data_dir.rglob('*') if f.is_file()]
        print(f"Found {len(all_files)} files in {data_dir}")
        return all_files

def get_repo_version(path=BASE_DIR):
    try:
        repo = git.Repo(path, search_parent_directories=True)
        sha = repo.head.commit.hexsha
        is_dirty = repo.is_dirty()
        branch = repo.active_branch.name if not repo.head.is_detached else "detached"
        remote = repo.remote(name='origin') if 'origin' in [r.name for r in repo.remotes] else repo.remotes[0]
        url = list(remote.urls)[0]
        repo_name = Path(url).stem

        meta_dict = {'Repo_name': repo_name,
                     'commit_sha': sha[:7],
                     'full_sha': sha,
                     'branch': branch,
                     'is_dirty': is_dirty,
                     'version_string' :f"{sha[:7]}{'-dirty' if repo.is_dirty() else ''}"}
        
        return meta_dict
    except git.InvalidGitRepositoryError:
        return "not a git repo"

def dict_to_string(d: dict, indent: int = 0) -> str:
    """Formats a dictionary into clean key-value pairs line-by-line."""
    lines = []
    prefix = " " * indent
    for key, value in d.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(dict_to_string(value, indent + 4))
        else:
            lines.append(f"{prefix}{key}: {value}")
    return "\n".join(lines)

def list_to_string(items: list, bullet: str = "•") -> str:
    """Formats a list into a vertical bulleted list string."""
    return "\n".join(f"{bullet} {item}" for item in items)

def add_to_metadata(metastring, string_to_add, header=""):
    if header != "":
        metastring = f"{metastring}\n-----{header}-----\n{string_to_add}"
    else:
        metastring = f"{metastring}\n{string_to_add}"
    return metastring

def get_now():
    return datetime.now().isoformat()

def save_metadata():
    metastring = ""
    metastring = add_to_metadata(metastring, get_now(), "Code run datetime")
    metastring = add_to_metadata(metastring, dict_to_string(get_repo_version()), "Git repo data")
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(RAW_DATA_DIR)), 'Raw data files')
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(PROCESSED_DIR)), 'Processed data files')
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(PLOT_DIR)), 'Plot files')
           
    metastring_file = PLOT_DIR / "metadata.log"

    with open(metastring_file, 'w', encoding='utf-8') as f:
        f.write(metastring)
    return metastring

if __name__ == "__main__":
    print(save_metadata())