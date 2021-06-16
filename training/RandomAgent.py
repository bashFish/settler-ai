import copy
import pickle
import time

import numpy as np
from tensorflow.python.keras.utils import losses_utils

from building.sawmill import Sawmill
from building.woodcutter import Woodcutter
from control import Control
from events import GameEvent
from misc import parse_buildings
from state import State
import random
import csv

from training.DQNAgent import Agent


class RandomAgent(Agent):
    def __init__(self, discount_factor, reward_lookahead):
        super().__init__()
        self.best_moves

    def choose_action(self, state, environment):
        pass

    def train(self):
        pass

    def end_episode(self):
        pass

"""
if top_10_games[-1][0] > 0:
    if choice > .95:
        predict_key, _, coords = top_10_games[-1][1][i]
        print("best %s %s" % (predict_key, coords))
        moveTaken = True
        movetaker = 1
    elif choice > .70:
        predict_key, coords = get_best_player_move_randomized(s, i)
        print("random %s %s" % (predict_key, coords))
        moveTaken = True
        movetaker = 2

if predict_key is not None and predict_key_position is None:
    for ijk in range(5):
        if all_keys_model[ijk] == predict_key:
            building = tf.one_hot(ijk, 5)
            predict_key_position = ijk
"""