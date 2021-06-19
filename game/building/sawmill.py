from building.building import Building, BuildingFactory


class SawmillFactory(BuildingFactory):

    def instanciate(self, coordinate):
        return Sawmill(self._config, coordinate)


class Sawmill(Building):
    pass