import pytest

import numpy as np
from lab_analysis_system.instruments.spect_aurora_4000 import SpectAurora4000
from lab_analysis_system.instruments.spect_ocean_optics_uv import SpectOceanOpticsUV
from lab_analysis_system.instruments.osa_ando import OSAAndo
from lab_analysis_system.instruments.rfa_agilent import RFAAgilent
from lab_analysis_system.instruments.frog_mesa import FROGMesa




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
    assert parsed["source_file"] == aurora_file.name
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
    assert parsed["source_file"] == oo_file.name
    assert parsed["Scans to average"] == "5"
    assert parsed["Wavelength (nm)"] == [400.0, 405.0, 410.0]

def test_osa_ando_parse(tmp_path):
    osa_file = tmp_path / "001_HWP1_45_HWP2_90_QWP_0_500mA_test_20261029_153000.csv"
    osa_file.write_text("Wavelength,dBm\n795.0,1.0\n800.0,11.0\n", encoding="utf-8")

    parsed = OSAAndo().parse(osa_file)
    assert parsed["source_file"] == osa_file.name
    assert parsed["exp_index"] == 1
    assert parsed["HWP1"] == 45.0
    assert parsed["Wavelength (nm)"] == [795.0, 800.0]
    assert parsed["Power (mW)"] == [1.0, 11.0]


def test_rfa_agilent_parse(tmp_path):
    rf_file = tmp_path / "002_HWP1_10_HWP2_20_QWP_30_400mA_rf_note.csv"
    rf_file.write_text(
        "Date (day-month-year),29_10_2026\n"
        "Time (24h-minute-second),14_30_00\n"
        "Frequency,1000000.0,2000000.0\n"
        "Power,-50.0,-20.0\n",
        encoding="utf-8",
    )

    parsed = RFAAgilent().parse(rf_file)
    assert parsed["source_file"] == rf_file.name
    assert parsed["exp_index"] == 2
    assert parsed["Frequency (Hz)"] == [1000000.0, 2000000.0]
    assert parsed["Power (dBm)"] == [-50.0, -20.0]
    assert parsed["date"] == "2026-10-29T14:30:00"


def test_frog_mesa_parse(tmp_path):
    stamp = "10_29_time_15_33_12_717"
    stats_file = tmp_path / f"Pulse_Stats {stamp}.txt"
    stats_file.write_text(
        "Pulse Statistics\n"
        "Pulse Width: 45.2 fs\n"
        "Bandwidth: 12.5 nm\n"
        "Bandwidth: 5.1 THz\n"
        "TBW Product: 0.45\n"
        "FROG Trace Error: 0.0032\n",
        encoding="utf-8",
    )
    # Create the 3 required companion files
    (tmp_path / f"Pulse_Time_Domain {stamp}.txt").write_text("0.0 1.0 0.0\n10.0 0.5 0.0\n", encoding="utf-8")
    (tmp_path / f"Pulse_Complex_Time_Domain {stamp}.txt").write_text("0.0 1.0 0.1\n10.0 0.7 0.2\n", encoding="utf-8")
    (tmp_path / f"Pulse_Freq_Domain {stamp}.txt").write_text("800.0 1.0 0.0\n805.0 0.5 0.0\n", encoding="utf-8")

    parsed = FROGMesa().parse(stats_file)
    assert parsed["source_file"] == stats_file.name
    assert parsed["pulse_width"] == 45.2
    assert parsed["pulse_width_unit"] == "fs"
    assert parsed["bandwidth"] == 12.5
    assert parsed["bandwidth_thz"] == 5.1
    assert parsed["pulse_time_data_time"] == [0.0, 10.0]
    assert parsed["pulse_freq_data_wavelength"] == [800.0, 805.0] 


def test_spectrometers_analyze():
    raw_spectrum = {
        "Wavelength (nm)": np.linspace(-5, 5),
        "Power (mW)": np.exp(-(np.linspace(-5, 5)) ** 2),
    }

    for inst in (OSAAndo(), SpectAurora4000(), SpectOceanOpticsUV()):
        analyzed = inst.analyze(raw_spectrum.copy())
        assert "Center Wavelength (nm)" in analyzed
        assert analyzed['Center Wavelength (nm)'] == pytest.approx(0.0)
        assert "FWHM Wavelength (nm)" in analyzed
        assert np.isclose(np.max(analyzed["Normalized Linear Power (a.u.)"]), 1.0)
        assert np.isclose(np.min(analyzed["Normalized Linear Power (a.u.)"]), 0.0)


def test_non_spectral_instruments_analyze_passthrough():
    dummy_data = {"source_file": "sample.txt", "metric": 42}
    for inst in (RFAAgilent(), FROGMesa()):
        assert inst.analyze(dummy_data.copy()) == dummy_data