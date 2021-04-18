from building.barack import BarackFactory
from building.sawmill import SawmillFactory
from building.storehouse import StorehouseFactory


class Factory:
    def __init__(self, config):
        self.config = config
        print(config)
        self.barack_factory = BarackFactory(self.config['Barack'])
        self.sawmill_factory = SawmillFactory(self.config['Sawmill'])
        self.storehouse_factory = StorehouseFactory(self.config['Storehouse'])

    def create_building(self, name, coordinate):
        if name == "Barack":
            return self.barack_factory.instanciate(coordinate)
        if name == "Base":
            return None
        if name == "Sawmill":
            return self.sawmill_factory.instanciate(coordinate)
        if name == "Storehouse":
            return self.storehouse_factory.instanciate(coordinate)