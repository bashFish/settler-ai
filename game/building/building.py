from abc import ABC, abstractmethod


class BuildingFactory(ABC):
    def __init__(self, config):
        self._config = config

    @abstractmethod
    def instanciate(self, coordinate):
        pass

class Building(ABC):
    pass