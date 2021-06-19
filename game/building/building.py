import itertools
from abc import ABC, abstractmethod

from events import GameEvent


class BuildingFactory(ABC):
    def __init__(self, config):
        self._config = config

    @abstractmethod
    def instanciate(self, coordinate):
        pass


class Building(ABC):
    def __init__(self, config, coordinate):
        self.config = config
        self.coordinate = coordinate

        self.finished = False
        self.constructionTicks = self.config['construction']['ticks']
        self.requiredMaterial = list(itertools.chain(*[[c]*self.config['construction']['cost'][c] for c in self.config['construction']['cost']]))
        self.constructionMaterial = []
        self.workMaterial = []
        self.doneMaterial = []
        self.currentMaterialTick = 0

        self.requiredWorkMaterial = self.config['consumes'] if 'consumes' in self.config else None
        self.productionMaterial = self.config['production']['good'] if 'production' in self.config else None
        self.materialTicks = self.config['production']['ticks'] if 'production' in self.config else None
        self.ressourceSearchRadius = self.config['searchradius'] if 'searchradius' in self.config else None


    def tick(self, state):
        if self.finished:
            if self.currentMaterialTick == 0:
                if len(self.doneMaterial) < 2:

                    # TODO: enforce exclusive or here?
                    if self.ressourceSearchRadius and state.findReduceRessource(self.productionMaterial,
                                                                                self.coordinate,
                                                                                self.ressourceSearchRadius):
                        self.currentMaterialTick = self.materialTicks

                    if self.requiredWorkMaterial and self.workMaterial:
                        self.workMaterial.pop(0)
                        self.currentMaterialTick = self.materialTicks
            else:
                self.currentMaterialTick -= 1
                if self.currentMaterialTick == 0:
                    self.doneMaterial.append(self.productionMaterial)

            if self.requiredWorkMaterial and len(self.workMaterial) < 3 and state.carrierAvailable() and state.materialAvailable('wood'):
                self.workMaterial.append(state.acquireMaterial(self.requiredWorkMaterial))
            if len(self.doneMaterial) and state.carrierAvailable():
                state.addMaterial(self.doneMaterial.pop(0))

        else:
            if self.constructionMaterial or not self.requiredMaterial:
                self.constructionTicks -= 1
                if self.constructionTicks <= 0:
                    self.finished = True
                    # TODO: should a building be able to throw an event???
                    state.add_game_event(GameEvent._ADD_BUILDING, (self.coordinate, self.__class__.__name__))
                if self.constructionMaterial:
                    self.constructionMaterial.pop(0)
            if self.requiredMaterial and state.carrierAvailable() and state.materialAvailable(self.requiredMaterial[0]):
                self.constructionMaterial.append(state.acquireMaterial(self.requiredMaterial.pop(0)))
