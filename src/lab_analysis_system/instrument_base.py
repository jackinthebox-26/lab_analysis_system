from abc import ABC, abstractmethod
from pathlib import Path

class Instrument(ABC):
    registry: list["Instrument"] = []

    def __init_subclass__(cls, **kwargs):
        """Automatically registers any class that inherits from Instrument."""
        super().__init_subclass__(**kwargs)
        Instrument.registry.append(cls())


    @property
    @abstractmethod
    def name(self) -> str:
        """e.g., 'OSA' or 'Aurora 4000'"""
        pass

    @property
    @abstractmethod
    def config_key(self) -> str:
        """The exact key used in data_load_config.toml (e.g., 'OSA_data')."""
        pass

    @abstractmethod
    def can_identify(self, file_path: Path, first_5_lines: list[str]) -> bool:
        """Return True if this instrument generated this specific file."""
        pass