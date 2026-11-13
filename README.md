File Structure
```
lab_analysis_system/                      # Repository root (BASE_DIR)
├── pyproject.toml                        # Editable package definition (pip install -e .)
├── README.md
├── main.py                               # Full pipeline entrypoint
├── config/
│   ├── data_load_config.toml             # Target date folder, output paths, per-instrument filenames
│   ├── figure_config.toml                # Plot styling, axis labels, and info-box templates
│   └── plot_style.mplstyle               # (Optional) Global Matplotlib stylesheet
├── experiments/
│   ├── exp_date_template.py              # Boilerplate copied when a new date is run
│   └── exp_2026_10_29.py                 # Auto-created daily script for custom/exploratory plots
├── tests/
│   ├── test_data_loader.py               # Registry identification and JSON saving tests
│   ├── test_file_tools.py                # Safe cleanup and directory traversal tests
│   ├── test_instruments.py               # Per-instrument parsing, analysis, and plotting tests
│   ├── test_math_tools.py                # Bounded Gaussian fitting and FWHM conversion tests
│   ├── test_metadata.py                  # Provenance formatting helper tests
│   └── test_parsers.py                   # Filename experimental settings parser tests
└── src/
    └── lab_analysis_system/
        ├── __init__.py
        ├── config.py                     # Loads TOML configs and resolves BASE_DIR / RAW_DIR
        ├── data_loader.py                # Routes raw files to registered instruments and saves JSONs
        ├── file_tools.py                 # Safe directory cleanup (blocks deletion of RAW_DIR)
        ├── graph_default.py              # Iterates over registered instruments to generate diagnostic plots
        ├── instrument_base.py            # Abstract Instrument base class with auto-registration registry
        ├── instrument_tools.py           # Shared parsers, spectral fitting, and plot helpers
        ├── logger.py                     # Configures console and file logging handlers
        ├── math_tools.py                 # Bounded Gaussian curve fitting and FWHM conversions
        ├── metadata.py                   # Records Git SHA, dirty state, and resolved file manifests
        ├── plot_helper.py                # Helper utilities imported by daily experiments/*.py scripts
        └── instruments/
            ├── __init__.py               # Imports all instrument plugins to trigger registration
            ├── frog_mesa.py              # Mesa FROG pulse stats and domain parser/plotter
            ├── osa_ando.py               # Ando OSA optical spectrum parser/analyzer/plotter
            ├── rfa_agilent.py            # Agilent RF spectrum analyzer parser/plotter
            ├── spect_aurora_4000.py      # Aurora 4000 spectrometer parser/analyzer/plotter
            └── spect_ocean_optics_uv.py  # Ocean Optics UV spectrometer parser/analyzer/plotter

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

