File Structure
```
lab_analysis_system/                  # Repository root (BASE_DIR)
    ├── pyproject.toml                    # Editable package definition (pip install -e .)
    ├── README.md
    ├── main.py                           # Full pipeline entrypoint
    ├── config/
    │   ├── data_load_config.toml         # Target date folder, output paths, per-instrument filenames
    │   ├── figure_config.toml            # Plot styling, axis labels, and info-box templates
    │   └── plot_style.mplstyle           # (Optional) Global Matplotlib stylesheet
    ├── experiments/
    │   ├── exp_date_template.py          # Boilerplate copied when a new date is run
    │   └── exp_2026_10_29.py             # Auto-created daily script for custom/exploratory plots
    └── src/
        └── package/
            ├── __init__.py
            ├── config.py                 # Loads TOML configs and resolves BASE_DIR / RAW_DIR
            ├── data_loader.py            # Categorizes raw files by header/filename and saves JSONs
            ├── parsers.py                # Instrument-specific parsers and filename metadata extraction
            ├── data_analysis.py          # Gaussian fitting and power normalization
            ├── math_tools.py             # Bounded Gaussian curve fitting and FWHM conversions
            ├── graph_default.py          # Standard diagnostic plots with metadata info boxes
            ├── plot_helper.py            # Helper utilities imported by daily experiments/*.py scripts
            ├── file_tools.py             # Safe directory cleanup (blocks deletion of RAW_DIR)
            └── metadata.py               # Records Git SHA, dirty state, and resolved file manifests
```
How to install and start to work with this package
1. Create venv: python -m venv venv
2. Activate venv: 
    a. ctrl + shift + P
    b. Select Python:Select Interpretor
    c. Select venv in your workspace
3. Install this package: pip install -e .


To clean up everything 
1. git reset --hard HEAD
2. git clean -fdx

NOTE: git clean DELETES UNTRACKED FILES. DONT DO THIS BY ACCIDENT.


To go to an older version to re-create the plots
1. git checkout `<hash>`
2. Run main.py
3. git checkout main


To create an easilty sharable bundle use the following code in powershell
`
Get-ChildItem -Recurse -File -Include *.py, *.js, *.html, *.css, *.md, *.sql, *.toml | 
    Where-Object { $_.FullName -notmatch '[\\/](node_modules|\.git|venv)[\\/]' } | 
    ForEach-Object { "=== $($_.FullName) ==="; Get-Content $_.FullName -Raw; "`n" } | 
    Out-File -Encoding utf8 project_bundle.txt
    
    `


TODO
- Add logging
- Add unittests
- Make it easier to add instroments
- Make it easier to add instroments
