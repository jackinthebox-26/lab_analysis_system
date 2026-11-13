import pytest
from lab_analysis_system.instrument_tools import parse_OSC_settings

def test_parse_OSC_settings_valid_filename():
    filename = "001_HWP1_45dot5_HWP2_90_QWP_0_500mA_test_notes_20261029_153000.csv"
    settings = parse_OSC_settings(filename)
    
    assert settings["exp_index"] == 1
    assert settings["HWP1"] == 45.5
    assert settings["HWP2"] == 90.0
    assert settings["QWP"] == 0.0
    assert settings["Pump current"] == "500"
    assert settings["Notes"] == "test notes"
    assert "date" in settings

def test_parse_OSC_settings_missing_keys():
    # Missing HWP1 and Pump current
    filename = "002_HWP2_90_QWP_0_20261029_153000.csv"
    with pytest.raises(ValueError, match="missing required experimental settings"):
        parse_OSC_settings(filename)