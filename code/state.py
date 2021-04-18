import json
import numpy as np

from building.factory import Factory
from misc import parse_buildings
from events import UiEvent

buildings, _, _ = parse_buildings()

rows = 50
cols = 50

from abc import ABC, abstractmethod
class Building(ABC):
    @abstractmethod
    def process_tick(self):
        pass

#TODO: evnt queue
#TODO: wie heisst da paradigma fuer buildingqueue/process tick?
class State(object):
    def __init__(self):
        #TODO: not best-practice to do io in constructor
        with open('config/initial_state.json') as fp:
            self.state_dict = json.load(fp)

        self._ui_events = []
        self._game_events = []

        self.tick = 0
        self.latest_state_tick = 0

        self.landscape_occupation = np.zeros((rows, cols), np.int)
        self.landscape_resource_amount = np.zeros((rows, cols), np.int)
        self.owned_terrain = np.zeros((rows, cols), np.int)

        #TODO: are these state or to be moved to game?
        buildings_conf, _, _ = parse_buildings()
        self._building_factory = Factory(buildings_conf)
        self.buildings = []
        self.constructing_buildings = []

    def add_game_event(self, event, data=None):
        self._game_events.append((event, data))

    def add_ui_event(self, event, data=None):
        self._ui_events.append((event, data))

    def fetch_reset_ui_events(self):
        if not self._ui_events:
            return []

        events = self._ui_events
        self._ui_events = []
        return events

    def fetch_reset_game_events(self):
        if not self._game_events:
            return []

        events = self._game_events
        self._game_events = []
        return events

    def increment_tick(self):
        self.tick += 1
        for b in self.buildings:
            b.tick(self)

    def carrierAvailable(self):
        return True

    def materialAvailable(self, material):
        return self.state_dict[material] > 0

    def acquireMaterial(self, material):
        self.state_dict[material] -= 1
        # TODO: decrease carrier
        return material

    def addMaterial(self, material):
        self.state_dict[material] += 1

    def construct_building(self, coordinate, building):
        if self.landscape_occupation[coordinate] == 0 and self.owned_terrain[coordinate]:
            self.buildings.append(self._building_factory.create_building(building, coordinate))
            return True
        return False

    def do_add_building(self, coordinate, building):
        self.landscape_occupation[coordinate] = buildings[building]['objectid']
        #TODO:
        #self.buildings.append(self._building_factory.create_building(building, coordinate))

        if 'borderextend' in buildings[building]:
            extend = buildings[building]['borderextend']
            #TODO: check coordinates!
            self.owned_terrain[(coordinate[0] - extend):(coordinate[0] + extend + 1), (coordinate[1] - extend):(coordinate[1] + extend + 1)] = 1
            return 'extend'
        return True


    # TODO: seems like only proper methods are shareable thru process/manager :/
    def get_ticks(self):
        return self.tick, self.latest_state_tick

    def get_state_dict(self):
        return self.state_dict

    # TODO: seems to copy everything -> can this be efficient ??
    def get_landscape_occupation(self):
        return self.landscape_occupation

    def get_landscape_resource_amount(self):
        return self.landscape_resource_amount

    def get_owned_terrain(self):
        return self.owned_terrain

    def set_landscape_occupation(self, coords, state):
        self.landscape_occupation[coords] = state

    def set_landscape_occupation_complete(self, ls_occ):
        self.landscape_occupation = ls_occ

    def set_landscape_resource_amount_complete(self, ls_ra):
        self.landscape_resource_amount = ls_ra

    def __repr__(self):
        return "settler: %i  wood: %i  plank: %i\nticks: %i" % (self.settler, self.wood, self.plank)