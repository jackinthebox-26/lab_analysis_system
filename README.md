Lab Analysis System

Automated experimental data-processing, curve-fitting, and diagnostic plotting pipeline for multi-instrument ultrafast optics and spectroscopy experiments.

File Structure

lab_analysis_system/                      # Repository root (BASE_DIR)
├── pyproject.toml                        # Editable package definition, CLI entrypoint, and pytest config
├── README.md
├── main.py                               # Convenience entrypoint forwarding to lab_analysis_system.__main__
├── make_bundle.py                        # Bundles repository source/config files into project_bundle.txt
├── config/
│   ├── data_load_config.toml             # Default target date folder, output paths, per-instrument filenames
│   ├── figure_config.toml                # Plot styling, axis labels, and info-box templates
│   └── plot_style.mplstyle               # (Optional) Global Matplotlib stylesheet
├── experiments/
│   ├── exp_date_template.py              # Boilerplate auto-cloned when a new experiment date is run
│   └── exp_YYYY_MM_DD.py                 # Date-specific scripts for custom/exploratory analysis & plots
├── tests/
│   ├── test_data_loader.py               # Registry identification, JSON saving, and CLI path forwarding tests
│   ├── test_file_tools.py                # Safe cleanup (RAW_DIR protection) and directory traversal tests
│   ├── test_instruments.py               # Per-instrument parsing, analysis, and plotting tests
│   ├── test_main.py                      # End-to-end pipeline integration and bundle generation tests
│   ├── test_math_tools.py                # Bounded Gaussian fitting and FWHM conversion tests
│   ├── test_metadata.py                  # Provenance formatting helper tests
│   ├── test_parsers.py                   # Filename experimental settings parser tests
│   └── test_plot_helper.py               # Processed JSON-to-NumPy array loader tests
└── src/
    └── lab_analysis_system/
        ├── __init__.py
        ├── __main__.py                   # CLI argument parsing and full pipeline orchestration
        ├── config.py                     # Loads TOML configs and resolves BASE_DIR / RAW_DIR paths
        ├── data_loader.py                # Routes raw files to registered instruments and saves JSONs
        ├── file_tools.py                 # Safe directory cleanup (blocks deletion of RAW_DIR)
        ├── graph_default.py              # Iterates over registered instruments to generate diagnostic plots
        ├── instrument_base.py            # Abstract Instrument base class with __init_subclass__ registry
        ├── instrument_tools.py           # Shared parsers, spectral fitting, and plot helpers
        ├── logger.py                     # Configures console and file logging handlers
        ├── math_tools.py                 # Bounded Gaussian curve fitting and FWHM conversions
        ├── metadata.py                   # Records Git SHA, dirty state, and resolved file manifests
        ├── plot_helper.py                # Helper utilities imported by daily experiments/*.py scripts
        └── instruments/
            ├── __init__.py               # Imports all instrument plugins to trigger auto-registration
            ├── frog_mesa.py              # Mesa FROG pulse stats and temporal/spectral domain parser/plotter
            ├── osa_ando.py               # Ando OSA optical spectrum parser/analyzer/plotter
            ├── rfa_agilent.py            # Agilent RF spectrum analyzer parser/plotter
            ├── spect_aurora_4000.py      # Aurora 4000 spectrometer parser/analyzer/plotter
            └── spect_ocean_optics_uv.py  # Ocean Optics UV spectrometer parser/analyzer/plotter



Installation & Setup

Create a virtual environment:

python -m venv venv



Activate the virtual environment:

VS Code: Ctrl + Shift + P $\rightarrow$ Python: Select Interpreter $\rightarrow$ choose ./venv

PowerShell: .\venv\Scripts\Activate.ps1

macOS / Linux: source venv/bin/activate

Install the package in editable mode:

pip install -e .



Usage

Running the Analysis Pipeline

Run using the default folder in config/data_load_config.toml:

lab-analysis



(or python main.py)

Run for a specific experiment date (resolved relative to prefix_to_head in data_load_config.toml):

lab-analysis -d 2026-10-29



(Accepts YYYY-MM-DD, YYYY/MM/DD, or YYYY_MM_DD.)

Run on an explicit raw data directory:

lab-analysis --data-dir ../2026/10/29



Running Tests & Regenerating the Project Bundle

A single pytest command runs all unit tests, executes the end-to-end pipeline on the default dataset, and refreshes project_bundle.txt:

pytest



To generate project_bundle.txt standalone:

python make_bundle.py



Adding a New Instrument

Because Instrument uses __init_subclass__ auto-registration (src/lab_analysis_system/instrument_base.py), adding a new device requires no changes to the loader or plotting loops:

Create a new module in src/lab_analysis_system/instruments/ subclassing Instrument and implementing name, can_identify(), parse(), analyze(), and plot().

Import the new class in src/lab_analysis_system/instruments/__init__.py.

Add [<instrument_name>] entries (data_file, plot_folder, file_info, axis labels) to config/data_load_config.toml and config/figure_config.toml.

Reproducibility & Repository Maintenance

Recreating Figures from an Earlier Run

Every run writes a metadata_<sha>.log (or metadata_<sha>-dirty.log) file inside processed_data/ recording the exact Git commit SHA and file manifest. To reproduce historical plots:

Check out the recorded commit:

git checkout <hash>



Re-run the pipeline for that dataset:

lab-analysis -d YYYY-MM-DD



Return to main:

git checkout main



Hard Resetting Untracked Files

git reset --hard HEAD
git clean -fdx



Warning: git clean -fdx permanently deletes all untracked files (including virtual environments and local logs). Use with caution.

TODO

[ ] Add new instrument plugins and analysis routines as needed

[ ]