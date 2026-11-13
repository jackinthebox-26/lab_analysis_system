from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import pandas as pd

class Instrument(ABC):
    _registry: ClassVar[dict[str, type["Instrument"]]] = {}

    def __init_subclass__(cls, **kwargs):
        """Automatically registers any class that inherits from Instrument."""
        super().__init_subclass__(**kwargs)
        # Skip intermediate abstract base classes if any are added later
        if not getattr(cls, "__abstractmethods__", None):
            Instrument._registry[cls.__name__] = cls
        

    @classmethod
    def get_all_instruments(cls) -> list["Instrument"]:
        """Instantiate and return one instance of each registered instrument."""
        return [inst_cls() for inst_cls in cls._registry.values()]


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
    def plot(self, row: pd.Series) -> None:
        """Render and save the default diagnostic plot for one processed data row."""
        pass

    def should_ignore(self, file_path: Path) -> bool:
        """Return True for auxiliary/companion files handled alongside a primary file."""
        return False


    
    