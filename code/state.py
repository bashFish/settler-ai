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
        self.landscape_occupation = np.zeros((rows, cols), np.int)
        self.landscape_resource_amount = np.zeros((rows, cols), np.int)

        self.initialize()

    # TODO: should be moved into state!
    def initialize(self):

        # place wood
        for i in range(6):
            cell = (random.randint(0, rows-1), random.randint(0, cols-1))
            for j in range(10):
                x_d = random.randint(0,2)-1
                y_d = random.randint(0,2)-1
                cell = tuple(map(sum, zip(cell, (x_d,y_d))))
                if cell[0] < 0 or cell[1] < 0 or cell[0] >= cols or cell[1] >= rows:
                    continue
                self.landscape_occupation[cell[0], cell[1]] = 2
                self.landscape_resource_amount[cell[0], cell[1]] = 10

        middle = (int(rows / 2), int(cols / 2))

        self.landscape_occupation[(middle[0]-5):(middle[0]+5),(middle[1]-5):(middle[1]+5)] = 0
        self.landscape_resource_amount[(middle[0]-5):(middle[0]+5),(middle[1]-5):(middle[1]+5)] = 0

        self.buildings.append((middle, 'base'))
        self.landscape_occupation[middle[0], middle[1]] = 1  # building

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