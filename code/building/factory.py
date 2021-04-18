from building.barack import BarackFactory


class Factory:
    def __init__(self, config):
        self.config = config
        print(config)
        self.barack_factory = BarackFactory(self.config['Barack'])

    def create_building(self, name, coordinate):
        if name == "Barack":
            return self.barack_factory.instanciate(coordinate)
        if name == "Base":
            return None