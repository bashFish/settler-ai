import json
import numpy as np

from events import UiEvent

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

        self.buildings = []
        self.landscape_occupation = np.zeros((rows, cols), np.int)
        self.landscape_resource_amount = np.zeros((rows, cols), np.int)

    def add_game_event(self, event):
        self._game_events.append(event)

    def add_ui_event(self, event):
        self._ui_events.append(event)

    def fetch_reset_ui_events(self):
        events = self._ui_events
        self._ui_events = []
        return events

    def fetch_reset_game_events(self):
        events = self._game_events
        self._game_events = []
        return events

    def increment_tick(self):
        self.tick += 1
        self.add_ui_event(UiEvent.UpdateTick)

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

    def set_landscape_occupation(self, coords, state):
        self.landscape_occupation[coords] = state

    def set_landscape_occupation_complete(self, ls_occ):
        self.landscape_occupation = ls_occ

    def set_landscape_resource_amount_complete(self, ls_ra):
        self.landscape_resource_amount = ls_ra

    def __repr__(self):
        return "settler: %i  wood: %i  plank: %i\nticks: %i" % (self.settler, self.wood, self.plank)