import json
import random

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

        self.produced_dict = {'wood': 0, 'plank': 0}

        self._ui_events = []
        self._game_events = []

        self.tick = 0
        self.latest_state_tick = 0

        self.cut_wood = 0
        self.landscape_occupation = np.zeros((rows, cols), np.int)
        self.landscape_resource_amount = np.zeros((rows, cols), np.int)
        self.owned_terrain = np.zeros((rows, cols), np.int)

        #TODO: are these state or to be moved to game?
        buildings_conf, _, _ = parse_buildings()
        self._building_factory = Factory(buildings_conf)
        self.buildings = []
        self.availableCarrier = 0

        self.settler_score_penalty = 0

    def add_game_event(self, event, data=None):
        self._game_events.append((event, data))

    def add_ui_event(self, event, data=None):
        print("before" + str(data))
        self._ui_events.append((event, data))
        print("after")

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

    #TODO: should this be in game rather than state?
    def increment_tick(self):
        self.availableCarrier = self.state_dict['carrier']
        self.tick += 1
        self.settler_score_penalty += self.state_dict['settler']+self.get_num_constructions()*5 #10 was way too much, i guess
        #TODO: is order important?
        cur_buildings = self.buildings.copy()
        random.shuffle(cur_buildings)
        for b in cur_buildings:
            b.tick(self)
        self.state_dict['freeCarrier'] = self.availableCarrier

    def carrierAvailable(self):
        return self.availableCarrier > 0

    def materialAvailable(self, material):
        return self.state_dict[material] > 0

    def acquireMaterial(self, material):
        self.state_dict[material] -= 1
        #self.state_dict["consumed_%s"%(material)] += 1
        self.availableCarrier -= 1
        return material

    def addMaterial(self, material):
        self.state_dict[material] += 1
        self.produced_dict[material] += 1
        self.availableCarrier -= 1

    def check_coordinates_buildable(self, coordinate):
        return self.landscape_occupation[coordinate] == 0 and self.owned_terrain[coordinate] # and coordinate not in [b.coordinate for b in self.buildings]

    def construct_building(self, coordinate, building):
        if self.check_coordinates_buildable(coordinate):
            self.buildings.append(self._building_factory.create_building(building, coordinate))
            self.landscape_occupation[coordinate] = -buildings[building]['objectid']
            return True
        return False

    def do_add_building(self, coordinate, building):
        self.landscape_occupation[coordinate] = buildings[building]['objectid']
        #TODO:
        #self.buildings.append(self._building_factory.create_building(building, coordinate))

        if 'settler' in buildings[building]:
            self.state_dict['settler'] += buildings[building]['settler']
        if 'carrier' in buildings[building]:
            self.state_dict['carrier'] += buildings[building]['carrier']

        if 'borderextend' in buildings[building]:
            extend = buildings[building]['borderextend']
            #TODO: check coordinates!
            arr = self.reduceArrayToRadius(self.owned_terrain, coordinate, extend)
            arr[:,:] = 1
            #[(coordinate[0] - extend):(coordinate[0] + extend + 1), (coordinate[1] - extend):(coordinate[1] + extend + 1)] = 1
            return 'extend'
        return True

    def delete_at(self, cell):
        self.landscape_occupation[cell] = 0
        self.landscape_resource_amount[cell] = 0
        for i, b in enumerate(self.buildings): #TODO: make this lookup faster?
            if b.coordinate == cell:
                if 'settler' in b.config:
                    self.state_dict['settler'] -= b.config['settler']
                if 'carrier' in b.config:
                    self.state_dict['carrier'] -= b.config['carrier']
                del self.buildings[i]
        #TODO: should this event be thrown here?
        self.add_ui_event(UiEvent.DELETE_CELL, cell)

    def reduceArrayToRadius(self, array, coordinate, radius):
        init_x = (coordinate[0]-radius)
        init_y = (coordinate[1]-radius)
        if init_x < 0:
            init_x = 0
        if init_y < 0:
            init_y = 0
        return array[init_x:(coordinate[0]+radius+1),init_y:(coordinate[1]+radius+1)]

    def findReduceRessource(self, ressource, coordinate, radius):
        try_radius = [radius]
        if coordinate[0]-radius < 0:
            try_radius.append(coordinate[0])
        if coordinate[1]-radius < 0:
            try_radius.append(coordinate[1])
        if coordinate[0]+radius >= rows:
            try_radius.append(rows-coordinate[1])
        if coordinate[1]+radius >= cols:
            try_radius.append(cols-coordinate[1])
        for rad in sorted(set(try_radius)):
            if self.doFindReduceRessource(ressource, coordinate, rad):
                return True
        return False

    def doFindReduceRessource(self, ressource, coordinate, radius):
        ressourceid = 8 # wood
        occupation = self.reduceArrayToRadius(self.landscape_occupation, coordinate, radius)
        amount = self.reduceArrayToRadius(self.landscape_resource_amount, coordinate, radius)
        result = np.where(occupation == 8)
        if not len(result[0]):
            return False
        amount[result[0][0],result[1][0]] -= 1
        if amount[result[0][0],result[1][0]] == 0:
            occupation[result[0][0],result[1][0]] = 0
            #TODO: should this event be thrown here?
            self.add_ui_event(UiEvent.DELETE_CELL, (coordinate[0]+result[0][0]-(occupation.shape[0]-1)/2,coordinate[1]+result[1][0]-(occupation.shape[1]-1)/2))
        return True

    def get_num_constructions(self):
        return len([b for b in self.buildings if b.finished == False])

    # cut wood + explore is the objective
    #TODO: later: drop buildings
    # +self.state_dict['plank']*10+self.state_dict['wood']*5 #-(self.settler_score_penalty>>1)
    def get_score(self):
        return np.sum(self.owned_terrain)*2 + self.produced_dict['plank']*5 - self.tick

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