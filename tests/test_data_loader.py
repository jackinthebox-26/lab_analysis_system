import pandas as pd
import pytest
from lab_analysis_system import data_loader
from lab_analysis_system.data_loader import LabDataLoader

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
def test_initiate_data_saving_uses_registry(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    processed_dir = tmp_path / "processed"

    # Redirect output path away from real lab folders
    monkeypatch.setattr(data_loader, "PROCESSED_DATA_PATH", processed_dir)

    osa_file = raw_dir / "001_HWP1_45_HWP2_90_QWP_0_500mA_test_20261029_153000.csv"
    osa_file.write_text("Wavelength,dBm\n795.0,1.0\n800.0,11.0\n805.0,1.0\n", encoding="utf-8")

    loader = LabDataLoader(data_dir=raw_dir)
    loader.initiate_data_saving()

    expected_json = processed_dir / "OSA_data.json"
    assert expected_json.is_file()

    df = pd.read_json(expected_json)
    assert len(df) == 1
    assert df.iloc[0]["source_file"] == osa_file.name
    assert "Center Wavelength (nm)" in df.columns