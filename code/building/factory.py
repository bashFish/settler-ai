from building.barack import BarackFactory
from building.sawmill import SawmillFactory


class Factory:
    def __init__(self, config):
        self.config = config
        print(config)
        self.barack_factory = BarackFactory(self.config['Barack'])
        self.sawmill_factory = SawmillFactory(self.config['Sawmill'])

    def create_building(self, name, coordinate):
        if name == "Barack":
            return self.barack_factory.instanciate(coordinate)
        if name == "Base":
            return None
        if name == "Sawmill":
            return self.sawmill_factory.instanciate(coordinate)