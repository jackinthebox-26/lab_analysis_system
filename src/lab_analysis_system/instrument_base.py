from abc import ABC, abstractmethod
from pathlib import Path
import importlib.metadata

import pandas as pd

class Instrument(ABC):
    ENTRY_POINT_GROUP = "lab_analysis.instruments"

    @classmethod
    def get_all_instruments(cls) -> list["Instrument"]:
        """Discover, validate, and instantiate all registered instrument plugins."""
        instruments: list[Instrument] = []
        for ep in importlib.metadata.entry_points(group=cls.ENTRY_POINT_GROUP):
            inst_cls = ep.load()
            if not (isinstance(inst_cls, type) and issubclass(inst_cls, cls)):
                raise TypeError(
                    f"Entry point '{ep.name}' ({inst_cls!r}) must subclass Instrument."
                )
            inst = inst_cls()
            if inst.name != ep.name:
                raise ValueError(
                    f"Entry point name '{ep.name}' does not match {inst_cls.__name__}.name ('{inst.name}')."
                )
            instruments.append(inst)
        return instruments
    @property
    @abstractmethod
    def name(self) -> str:
        """e.g., 'OSA' or 'Aurora 4000'"""
        pass

    @abstractmethod
    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        """Return True if this instrument generated this specific file.
        Note: `first_5_lines` is always padded to length 5 with empty strings (`""`)
        by `LabDataLoader` for files shorter than 5 lines.
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> dict:
        """Extract metadata and raw arrays from file_path into a dictionary."""
        pass

    @abstractmethod
    def analyze(self, raw_data: dict) -> dict:
        """Optional post-parse mathematical analysis. Defaults to no-op."""
        return raw_data

    @abstractmethod
    def plot(self, row: pd.Series, figure_dir: str | Path | None = None) -> None:
        """Render and save the default diagnostic plot for one processed data row."""
        pass

    def should_ignore(self, file_path: Path) -> bool:
        """Return True for auxiliary/companion files handled alongside a primary file."""
        return False


    
    