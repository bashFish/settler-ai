import itertools

from building.building import Building, BuildingFactory

from events import GameEvent


class WoodcutterFactory(BuildingFactory):
    def __init__(self, config):
        self._config = config

    def instanciate(self, coordinate):
        return Woodcutter(self._config, coordinate)


class Woodcutter(Building):
    def __init__(self, config, coordinate):
        self.config = config
        self.coordinate = coordinate

        self.finished = False
        self.constructionTicks = self.config['construction']['ticks']
        self.requiredMaterial = list(itertools.chain(*[[c]*self.config['construction']['cost'][c] for c in self.config['construction']['cost']]))
        self.constructionMaterial = []
        self.doneMaterial = []
        self.currentMaterialTick = 0

    def tick(self, state):
        if self.finished:
            if self.currentMaterialTick == 0:
                if len(self.doneMaterial) < 2:
                    if state.findReduceRessource('wood', self.coordinate, 6):
                        self.currentMaterialTick = 3
            else:
                self.currentMaterialTick -= 1
                if self.currentMaterialTick == 0:
                    self.doneMaterial.append('wood')
            if len(self.doneMaterial) and state.carrierAvailable():
                state.addMaterial(self.doneMaterial.pop(0))
        else:
            if self.constructionMaterial or not self.requiredMaterial:
                self.constructionTicks -= 1
                if self.constructionTicks <= 0:
                    self.finished = True
                    #TODO: should a building be able to throw an event???
                    state.add_game_event(GameEvent._ADD_BUILDING, (self.coordinate, self.__class__.__name__))
            if self.requiredMaterial and state.carrierAvailable() and state.materialAvailable(self.requiredMaterial[0]):
                self.constructionMaterial.append(state.acquireMaterial(self.requiredMaterial.pop(0)))
