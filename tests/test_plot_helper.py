import pytest
import pandas as pd
import numpy as np

from lab_analysis_system import plot_helper

def test_load_all_data_uses_registry(tmp_path, monkeypatch):
    monkeypatch.setattr(plot_helper, "PROCESSED_DATA_PATH", tmp_path)

    # Must not fall back to real PROCESSED_DATA_PATH when tmp_path is empty
    assert plot_helper.load_all_data() == {}

    sample_df = pd.DataFrame([
        {"source_file": "test.csv", "Wavelength (nm)": [800.0, 805.0]}
    ])
    sample_df.to_parquet(tmp_path / "OSA_data.parquet")

    loaded = plot_helper.load_all_data()
    assert "osa_ando" in loaded
    assert isinstance(loaded["osa_ando"]["Wavelength (nm)"].iloc[0], np.ndarray)