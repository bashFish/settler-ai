import pickle

from events import GameEvent
from misc import path_append
from training.agents.Agent import Agent
import random
import numpy as np

from training.misc.training_misc import get_current_timestring, NUM_EPISODE_HORIZON_OBSERVED


class RandomAgent(Agent):
    def __init__(self, epsilon_greedy = .1, move_selection = None):
        super().__init__()
        self.best_game = ([None]*NUM_EPISODE_HORIZON_OBSERVED, -99999)
        self.epsilon_greedy = epsilon_greedy
        self.current_action = -1
        self.choosable_keys = self.building_keys + ['-']
        if move_selection:
            self.move_selection = move_selection
        else:
            self.move_selection = self.random_action

    def __repr__(self):
        return "RandomAgent/ my best move: %s" % (str(self.best_game))

    def random_action(self, environment):
        key = random.choice(self.choosable_keys)
        if key == '-':
            return None

        possible = np.where(environment.get_owned_terrain() == 1)

        for _ in range(10):
            position = random.randint(0, len(possible[0])-1)
            x, y = possible[0][position], possible[1][position]
            cell = (x, y)

            if environment.check_coordinates_buildable(cell):
                break

        building = self.key_to_building[key]

        return (GameEvent.CONSTRUCT_BUILDING, (cell, building))

    def choose_action(self, environment):
        self.current_action += 1
        key, cell = None, None

        if random.random() < self.epsilon_greedy:
            return self.move_selection(environment)
        else:
            return self.best_game[0][self.current_action]

    def end_episode(self):
        current_score = self.current_episode_trajectories[-1][0]

        if current_score > self.best_game[1]:
            current_game = [c[2] for c in self.current_episode_trajectories]
            self.best_game = (current_game, current_score)

        self.current_episode_trajectories = []
        self.current_action = -1

    def train(self):
        pass

    def save(self):
        pickle.dump(self.best_game, open(path_append('training/models/random/%s.pckl'%(get_current_timestring())), 'wb'))

    def load(self, time_string):
        pickle.load(open(path_append('training/models/random/%s.pckl'%(time_string)),'rb'))