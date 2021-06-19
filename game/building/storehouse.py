from building.building import Building, BuildingFactory


class StorehouseFactory(BuildingFactory):

    def instanciate(self, coordinate):
        return Storehouse(self._config, coordinate)


class Storehouse(Building):
    pass