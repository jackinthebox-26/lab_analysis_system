from pathlib import Path

INCLUDE_EXTS = {".py", ".js", ".html", ".css", ".md", ".sql", ".toml"}
EXCLUDE_DIRS = {"node_modules", ".git", "venv", ".venv", "__pycache__", ".pytest_cache"}
OUTPUT_FILE = Path("project_bundle.txt")

bundle_preamble = """
================================================================================
PROJECT BUNDLE
================================================================================
GOAL:
This project is an automated experimental data-processing and plotting pipeline
designed to ingest raw lab instrument measurements, standardize and analyze them,
generate diagnostic and experiment-specific figures, and log reproducible
provenance metadata.

HOW THIS BUNDLE IS GENERATED:
- Recursively collects text/code files (`.py`, `.js`, `.html`, `.css`, `.md`,
  `.sql`, `.toml`) from the repository while excluding environments, caches,
  and version-control metadata (`venv`, `.git`, `__pycache__`, `.pytest_cache`,
  `node_modules`).
- Each file is delimited by a `=== <full_path> ===` header followed by its full
  raw contents.
- Use this bundle as the authoritative source of truth for the project's
  structure, configuration, and code before proposing edits or answering questions.
================================================================================
"""


def create_bundle(root: Path = Path.cwd(), output_file: Path = OUTPUT_FILE) -> None:
    root = root.resolve()
    files = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in INCLUDE_EXTS
        and not any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts)
    )

    with output_file.open("w", encoding="utf-8", newline="\n") as out:
        out.write(bundle_preamble)
        for file_path in files:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            out.write(f"=== {file_path} ===\n{content}\n\n")

    print(f"Bundled {len(files)} files into {output_file.resolve()}")


if __name__ == "__main__":
    create_bundle()