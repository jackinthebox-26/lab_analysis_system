from abc import ABC, abstractmethod

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
