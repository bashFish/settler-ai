from building.building import Building, BuildingFactory


class BarackFactory(BuildingFactory):

    def instanciate(self, coordinate):
        return Barack(self._config, coordinate)


class Barack(Building):
    pass