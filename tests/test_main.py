from lab_analysis_system.__main__ import main
import sys

from make_bundle import create_bundle

def test_make_bundle():
    create_bundle()
    
def test_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["lab-analysis"])
    main()
    