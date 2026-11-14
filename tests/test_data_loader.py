import pandas as pd
import pytest
from lab_analysis_system import data_loader
from lab_analysis_system.data_loader import LabDataLoader

import json
from pathlib import Path
from lab_analysis_system import __main__ as cli_main

import importlib.metadata
from lab_analysis_system.instrument_base import Instrument


def test_entry_point_plugin_discovery():
    instruments = Instrument.get_all_instruments()
    expected_names = {
        "frog_mesa",
        "osa_ando",
        "rfa_agilent",
        "spect_aurora_4000",
        "spect_ocean_optics_uv",
    }

    assert all(isinstance(inst, Instrument) for inst in instruments)
    assert {inst.name for inst in instruments} == expected_names


def test_entry_point_rejects_non_instrument_subclass(monkeypatch):
    bad_ep = importlib.metadata.EntryPoint(
        name="not_an_instrument",
        value="builtins:dict",
        group=Instrument.ENTRY_POINT_GROUP,
    )
    monkeypatch.setattr(importlib.metadata, "entry_points", lambda group: [bad_ep])

    with pytest.raises(TypeError, match="must subclass Instrument"):
        Instrument.get_all_instruments()


def test_entry_point_rejects_mismatched_name(monkeypatch):
    mismatched_ep = importlib.metadata.EntryPoint(
        name="wrong_config_key",
        value="lab_analysis_system.instruments.osa_ando:OSAAndo",
        group=Instrument.ENTRY_POINT_GROUP,
    )
    monkeypatch.setattr(importlib.metadata, "entry_points", lambda group: [mismatched_ep])

    with pytest.raises(ValueError, match="does not match OSAAndo.name"):
        Instrument.get_all_instruments()

def test_get_data_type_aurora(tmp_path):
    # Create a temporary file mimicking an Aurora 4000 output
    test_file = tmp_path / "test_aurora.txt"
    test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nDevice Name:Aurora 4000\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    data_type = loader.get_data_type(test_file)
    
    assert data_type == "spect_aurora_4000"

def test_get_data_type_ocean_optics(tmp_path):
    test_file = tmp_path / "test_oo.txt"
    test_file.write_text("1\n2\n3\n4\nSpectrometer: HR600944\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "spect_ocean_optics_uv"

def test_get_data_type_rf_analyser(tmp_path):
    test_file = tmp_path / "test_rf.csv"
    test_file.write_text("Date (day-month-year),2026-10-29\nLine 2\nLine 3\nLine 4\nLine 5\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "rfa_agilent"

def test_get_data_type_osa(tmp_path):
    test_file = tmp_path / "test_osa.csv"
    test_file.write_text("Wavelength,dBm\n800,-20\nLine 3\nLine 4\nLine 5\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "osa_ando"

def test_get_data_type_frog(tmp_path):
    test_file = tmp_path / "Pulse_Stats.csv"
    test_file.write_text("test")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "frog_mesa"

def test_get_data_type_unknown(tmp_path):
    test_file = tmp_path / "random_notes.txt"
    test_file.write_text("Just\nsome\nrandom\ntext\nhere\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "Other"

@pytest.mark.filterwarnings("ignore:Covariance of the parameters could not be estimated:scipy.optimize.OptimizeWarning")
def test_initiate_data_saving_uses_registry(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    processed_dir = tmp_path / "processed"

    osa_file = raw_dir / "001_HWP1_45_HWP2_90_QWP_0_500mA_test_20261029_153000.csv"
    osa_file.write_text("Wavelength,dBm\n795.0,1.0\n800.0,11.0\n805.0,1.0\n", encoding="utf-8")

    loader = LabDataLoader(data_dir=raw_dir, processed_dir=processed_dir)
    loader.initiate_data_saving()

    expected_parquet = processed_dir / "OSA_data.parquet"
    assert expected_parquet.is_file()

    df = pd.read_parquet(expected_parquet)
    assert len(df) == 1
    assert df.iloc[0]["source_file"] == osa_file.name
    assert "Center Wavelength (nm)" in df.columns



def test_run_daily_custom_plots_forwards_paths(tmp_path, monkeypatch):
    # Point BASE_DIR to tmp_path so run_daily_custom_plots looks in tmp_path/experiments
    monkeypatch.setattr(cli_main, "BASE_DIR", tmp_path)
    experiments_dir = tmp_path / "experiments"
    experiments_dir.mkdir()

    raw_dir = tmp_path / "data" / "2026" / "11" / "05"
    raw_dir.mkdir(parents=True)
    processed_dir = raw_dir / "processed_data"
    figure_dir = raw_dir / "plots"

    # Create a custom experiment script that records the arguments it receives
    marker_file = tmp_path / "received_args.json"
    script_path = experiments_dir / "exp_2026_11_05.py"
    script_path.write_text(
        "import json\n"
        "from pathlib import Path\n\n"
        "def main(processed_dir: Path, figure_dir: Path):\n"
        f"    Path(r'{marker_file}').write_text(json.dumps({{\n"
        "        'processed_dir': str(processed_dir),\n"
        "        'figure_dir': str(figure_dir),\n"
        "    }))\n",
        encoding="utf-8",
    )

    cli_main.run_daily_custom_plots(
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        figure_dir=figure_dir,
    )

    assert marker_file.is_file()
    recorded = json.loads(marker_file.read_text(encoding="utf-8"))
    assert Path(recorded["processed_dir"]) == processed_dir
    assert Path(recorded["figure_dir"]) == figure_dir


def test_run_daily_custom_plots_legacy_zero_arg_main(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_main, "BASE_DIR", tmp_path)
    experiments_dir = tmp_path / "experiments"
    experiments_dir.mkdir()

    raw_dir = tmp_path / "data" / "2026" / "11" / "06"
    raw_dir.mkdir(parents=True)
    processed_dir = raw_dir / "processed_data"
    figure_dir = raw_dir / "plots"

    marker_file = tmp_path / "legacy_ran.txt"
    script_path = experiments_dir / "exp_2026_11_06.py"
    script_path.write_text(
        "from pathlib import Path\n\n"
        "def main():\n"
        f"    Path(r'{marker_file}').write_text('ok')\n",
        encoding="utf-8",
    )

    cli_main.run_daily_custom_plots(
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        figure_dir=figure_dir,
    )

    assert marker_file.read_text(encoding="utf-8") == "ok"