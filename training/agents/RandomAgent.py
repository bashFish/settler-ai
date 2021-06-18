import pickle

from events import GameEvent
from training.agents.Agent import Agent
import random
import numpy as np


class RandomAgent(Agent):
    def __init__(self, epsilon_greedy = .1):
        super().__init__()
        self.best_game = None
        self.epsilon_greedy = epsilon_greedy
        self.current_action = -1
        self.choosable_keys = self.building_keys + ['-']

    def __repr__(self):
        return "RandomAgent/ my best move: %s" % (str(self.best_game))

    def choose_action(self, environment):
        self.current_action += 1
        key, cell = None, None

        if random.random() < self.epsilon_greedy or not self.best_game:
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
        else:
            return self.best_game[0][self.current_action]

    def end_episode(self):
        current_score = self.current_episode_trajectories[-1][0]

        if not self.best_game or current_score > self.best_game[1]:
            current_game = [c[2] for c in self.current_episode_trajectories]
            self.best_game = (current_game, current_score)

        self.current_episode_trajectories = []
        self.current_action = -1

    def train(self):
        pass

    def save(self):
        pickle.dump(self.best_game, open('models/__.pckl', 'wb'))

    def load(self):
        pickle.load(open('models/__.pckl'))