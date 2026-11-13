from pathlib import Path

INCLUDE_EXTS = {".py", ".js", ".html", ".css", ".md", ".sql", ".toml"}
EXCLUDE_DIRS = {"node_modules", ".git", "venv", ".venv", "__pycache__", ".pytest_cache"}
OUTPUT_FILE = Path("project_bundle.txt")


def create_bundle(root: Path = Path.cwd(), output_file: Path = OUTPUT_FILE) -> None:
    root = root.resolve()
    files = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in INCLUDE_EXTS
        and not any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts)
    )

    with output_file.open("w", encoding="utf-8", newline="\n") as out:
        for file_path in files:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            out.write(f"=== {file_path} ===\n{content}\n\n")

    print(f"Bundled {len(files)} files into {output_file.resolve()}")


if __name__ == "__main__":
    create_bundle()