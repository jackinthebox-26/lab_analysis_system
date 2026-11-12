from package.data_loader import LabDataLoader

def test_get_data_type_aurora(tmp_path):
    # Create a temporary file mimicking an Aurora 4000 output
    test_file = tmp_path / "test_aurora.txt"
    test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nDevice Name:Aurora 4000\n", encoding="utf-8")
    
    loader = LabDataLoader(data_dir=tmp_path)
    data_type = loader.get_data_type(test_file)
    
    assert data_type == "Aurora 4000"