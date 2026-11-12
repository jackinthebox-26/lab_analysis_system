from package.data_loader import LabDataLoader

def test_get_data_type_aurora(tmp_path):
    # Create a temporary file mimicking an Aurora 4000 output
    test_file = tmp_path / "test_aurora.txt"
    test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nDevice Name:Aurora 4000\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    data_type = loader.get_data_type(test_file)
    
    assert data_type == "Aurora 4000"

def test_get_data_type_ocean_optics(tmp_path):
    test_file = tmp_path / "test_oo.txt"
    test_file.write_text("1\n2\n3\n4\nSpectrometer: HR600944\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "Ocean Optics"

def test_get_data_type_rf_analyser(tmp_path):
    test_file = tmp_path / "test_rf.csv"
    test_file.write_text("Date (day-month-year),2026-10-29\nLine 2\nLine 3\nLine 4\nLine 5\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "RF analyser"

def test_get_data_type_osa(tmp_path):
    test_file = tmp_path / "test_osa.csv"
    test_file.write_text("Wavelength,dBm\n800,-20\nLine 3\nLine 4\nLine 5\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "OSA"

def test_get_data_type_unknown(tmp_path):
    test_file = tmp_path / "random_notes.txt"
    test_file.write_text("Just\nsome\nrandom\ntext\nhere\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    assert loader.get_data_type(test_file) == "Other"