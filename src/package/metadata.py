from datetime import datetime
import tomllib
from pathlib import Path


import git

from package.config import BASE_DIR, RAW_DIR, PROCESSED_DATA_PATH, FIGURE_PATH

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
        return {"Repo_name": "not a git repo"}

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
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(RAW_DIR)), 'Raw data files')
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(PROCESSED_DATA_PATH)), 'Processed data files')
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(FIGURE_PATH)), 'Plot files')
           
    metastring_file = FIGURE_PATH / "metadata.log"

    with open(metastring_file, 'w', encoding='utf-8') as f:
        f.write(metastring)
    return metastring

if __name__ == "__main__":
    print(save_metadata())