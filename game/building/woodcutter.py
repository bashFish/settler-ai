from building.building import Building, BuildingFactory


class WoodcutterFactory(BuildingFactory):

    def instanciate(self, coordinate):
        return Woodcutter(self._config, coordinate)


class Woodcutter(Building):
    pass
