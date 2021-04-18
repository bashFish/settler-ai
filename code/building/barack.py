from building.building import Building, BuildingFactory


class BarackFactory(BuildingFactory):
    def __init__(self, config):
        self._config = config

    def instanciate(self, coordinate):
        return Barack(self._config, coordinate)


class Barack(Building):
    def __init__(self, config, coordinate):
        pass
