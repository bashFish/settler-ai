import json
import numpy as np
import random

rows = 50
cols = 50

from abc import ABC, abstractmethod
class Building(ABC):
    @abstractmethod
    def process_tick(self):
        pass


class State:
    def __init__(self):
        with open('config/initial_state.json') as fp:
            self.state_dict = json.load(fp)

        self.buildings = []
        self.landscape_resource = np.array(rows, cols)
        self.landscape_resource_amount = np.array(rows, cols)

    # TODO: should be moved into state!
    def initialize(self):
        middle = (rows / 2, cols / 2)
        self.buildings.append(middle, 'base')

        # place wood
        for i in range(4):
            cell = (random.randint(0,rows), random.randint(0,cols))
            self.landscape_resource[cell[0],cell[1]] = 1 #wood
            self.landscape_resource_amount[cell[0],cell[1]] = 10

    @property
    def settler(self):
        return self.state_dict['settler']

    @property
    def wood(self):
        return self.state_dict['wood']

    @property
    def plank(self):
        return self.state_dict['plank']

    def __repr__(self):
        return "settler: %i  wood: %i  plank: %i" % (self.settler, self.wood, self.plank)