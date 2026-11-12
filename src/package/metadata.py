from datetime import datetime
from pathlib import Path

import git

from package.config import BASE_DIR, RAW_DIR, PROCESSED_DATA_PATH, FIGURE_PATH
from package.file_tools import find_all_files


def get_repo_hash(path=BASE_DIR):
    repo = git.Repo(path, search_parent_directories=True)
    sha = repo.head.commit.hexsha
    is_dirty = repo.is_dirty()
    return sha, is_dirty
    

def get_repo_version(path=BASE_DIR):
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

def list_to_string(items: list, bullet: str = "-") -> str:
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
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(RAW_DIR, nested=False, resolve=True)), 'Raw data files')
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(PROCESSED_DATA_PATH, nested=True, resolve=True)), 'Processed data files')
    metastring = add_to_metadata(metastring, list_to_string(find_all_files(FIGURE_PATH, nested=True, resolve=True)), 'Plot files')


    git_hash, is_dirty = get_repo_hash()

    if is_dirty:
        print("Warning: Git repository is dirty. Changes may not be tracked.")
        metastring_file = FIGURE_PATH / f"metadata_{git_hash[:7]}-dirty.log"
    else:
        metastring_file = FIGURE_PATH / f"metadata_{git_hash[:7]}.log"

    with open(metastring_file, 'w', encoding='utf-8') as f:
        f.write(metastring)
    return metastring

if __name__ == "__main__":
    print(save_metadata())