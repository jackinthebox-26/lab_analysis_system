import numpy as np
from lab_analysis_system.instruments.spect_aurora_4000 import SpectAurora4000
from lab_analysis_system.instruments.spect_ocean_optics_uv import SpectOceanOpticsUV

def test_aurora_parse_and_analyze(tmp_path):
    aurora_file = tmp_path / "aurora_sample.txt"
    aurora_file.write_text(
        "Header 1\n"
        "Integral Time(s): 0.05\n"
        "Avg Count: 10\n"
        "Other Description: Test run\n"
        "Device Name:Aurora 4000\n"
        "+++++Begin Spectral Data+++++\n"
        "795.0\t1.0\n"
        "800.0\t11.0\n"
        "805.0\t1.0\n",
        encoding="utf-8"
    )

    inst = SpectAurora4000()
    parsed = inst.parse(aurora_file)
    assert parsed["file_path"] == aurora_file.name
    assert parsed["Integral Time(s)"] == "0.05"
    assert parsed["Wavelength (nm)"] == [795.0, 800.0, 805.0]
    assert parsed["Power (mW)"] == [1.0, 11.0, 1.0]

   

def test_ocean_optics_parse_and_analyze(tmp_path):
    oo_file = tmp_path / "oo_sample.txt"
    oo_file.write_text(
        "Header 1\n"
        "Integration Time (sec): 0.1\n"
        "Scans to average: 5\n"
        "Line 4\n"
        "Spectrometer: HR600944\n"
        ">>>>>Begin Spectral Data<<<<<\n"
        "400.0\t2.0\n"
        "405.0\t12.0\n"
        "410.0\t2.0\n",
        encoding="utf-8"
    )

    inst = SpectOceanOpticsUV()
    parsed = inst.parse(oo_file)
    assert parsed["file_path"] == oo_file.name
    assert parsed["Scans to average"] == "5"
    assert parsed["Wavelength (nm)"] == [400.0, 405.0, 410.0]

    