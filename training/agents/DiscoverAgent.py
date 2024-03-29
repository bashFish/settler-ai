import pickle
from collections import deque

from events import GameEvent
from misc import path_append
from training.agents.Agent import Agent
import random
import numpy as np

from training.misc.game_misc import is_state_dead_end
from training.misc.training_misc import get_current_timestring, NUM_EPISODE_HORIZON_OBSERVED, \
    get_pseudo_random_position, TRAIN_MEMORY_SIZE, get_memory_from_current_episode, NUM_EPISODE_HORIZON_CONTROLLED


class DiscoverAgent(Agent):
    def __init__(self, discount_factor=0.9, reward_lookahead=10, epsilon_greedy = .1, move_selection = None, complete_random_threshold = .01):
        super().__init__()

        self.building_list = [['s'], ['w', 'k','-'], ['w', 'k','-'], ['s', 'w', 'k','-']]
        self.current_built_nr = 0

        self.replay_memory = deque(maxlen=TRAIN_MEMORY_SIZE)
        self.epsilon_greedy = epsilon_greedy
        self.discount_factor = discount_factor
        self.reward_lookahead = reward_lookahead
        self.complete_random_threshold = complete_random_threshold
        self.current_action = -1
        self.choosable_keys = self.building_keys + ['-']
        if move_selection:
            self.move_selection = move_selection
        else:
            self.move_selection = self.get_random_action
        self.top_10_games = [(-99999, [None]*NUM_EPISODE_HORIZON_CONTROLLED)]
        self.picked_game = self.top_10_games[0]

    def __repr__(self):
        return "RandomAgent/ my best games: %s" % (str(self.top_10_games))

    def get_random_action(self, environment):
        cur_build_pos = self.current_built_nr
        if self.current_built_nr >= len(self.building_list):
            cur_build_pos = len(self.building_list)-1

        current_choosable = self.building_list[cur_build_pos]
        key = random.choice(current_choosable)
        if key == '-':
            return None

        cell = get_pseudo_random_position(environment, key, self.complete_random_threshold)
        building = self.key_to_building[key]

        self.current_built_nr += 1
        return (GameEvent.CONSTRUCT_BUILDING, (cell, building))

    def choose_action(self, environment, inhibit_random = False):
        self.current_action += 1

        if not inhibit_random and random.random() < self.epsilon_greedy:
            return self.move_selection(environment)
        else:
            return self.picked_game[1][self.current_action]

    def update_top_10_games(self):

        current_score = self.current_episode_trajectories[-1][0]

        if is_state_dead_end(self.current_episode_trajectories[-1][1], self.buildings):
            top_10_moves = [c[1] for c in self.top_10_games]
            current_moves = [c[2] for c in self.current_episode_trajectories]
            if current_moves in top_10_moves:
                ind = top_10_moves.index(current_moves)
                if ind > 0:
                    del self.top_10_games[ind]
        elif current_score > max([c[0] for c in self.top_10_games]):
            current_game = [c[2] for c in self.current_episode_trajectories]
            self.top_10_games.append((current_score, current_game))
            self.top_10_games.sort(reverse=True)
            if len(self.top_10_games) > 10:
                del self.top_10_games[-1]

    def end_episode(self, print_trajectory):
        if print_trajectory:
            print("score: %s"%(self.current_episode_trajectories[-1][0]))
            print([x[2] for x in self.current_episode_trajectories])

        print([c[2] for c in self.current_episode_trajectories])
        new_memory = get_memory_from_current_episode(self.current_episode_trajectories, self.buildings,
                                                                  self.discount_factor, self.reward_lookahead)
        self.replay_memory.extend(new_memory)

        self.update_top_10_games()

        self.current_episode_trajectories = []
        self.current_action = -1
        self.current_built_nr = 0

        self.picked_game = random.choice(self.top_10_games)

    def train(self):
        pass

    def save(self, suffix=''):
        model_name = "%s_%s"%(get_current_timestring(),suffix)
        print("model number %s" %(model_name))
        pickle.dump(self.top_10_games, open(path_append('training/models/random/%s.pckl'%(model_name)), 'wb'))
        pickle.dump(self.replay_memory, open(path_append('training/models/random/%s_replay_memory.pckl'%(model_name)), 'wb'))

    def load(self, time_string):
        pickle.load(open(path_append('training/models/random/%s.pckl'%(time_string)), 'rb'))
