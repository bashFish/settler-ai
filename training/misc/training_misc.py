import tensorflow as tf
import time
import pickle
import copy
import numpy as np

from control import Control
from environment import Environment
from misc import path_append
import random
from training.misc.game_misc import is_state_dead_end

ACTION_SPACE = 5
ENVIRONMENT_DIMENSION = (50, 50)

TRAIN_MODEL_NAME = 'first_shot'
TRAIN_MINIBATCH_SIZE = 24
TRAIN_MIN_REPLAY_MEMORY_SIZE = 100
TRAIN_MEMORY_SIZE = 10000
TRAIN_UPDATE_TARGET_STEPS = 50
NUM_EPISODES = 1000
NUM_EPISODE_HORIZON_OBSERVED = 50
NUM_EPISODE_HORIZON_CONTROLLED = 25


def get_memory_from_current_episode(current_episode_trajectories, buildings, discount_factor, reward_lookahead):
    # computes reward from score (or dead end)
    # returns [[ state action nextstate reward ]_i for i]

    # 1st case: dead end -> rate entire X steps from trajectory with discount 'as bad'
    if is_state_dead_end(current_episode_trajectories[-1][1], buildings):
        last_good_index = len(current_episode_trajectories) - 2
        while last_good_index > 0:
            if not is_state_dead_end(current_episode_trajectories[last_good_index][1], buildings):
                break
            last_good_index -= 1

        resultset = []
        for i in range(last_good_index):
            current_reward = 0
            if not current_episode_trajectories[i][2]:
                current_reward -= .1
            resultset.append(list(current_episode_trajectories[i][1:]) + [current_reward, 0])
        resultset.append(list(current_episode_trajectories[last_good_index][1:]) + [-5, 1])

        return resultset

    resultset = []
    for i in range(NUM_EPISODE_HORIZON_CONTROLLED-1):
            current_reward = 0
            if not current_episode_trajectories[i][2]:
                current_reward -= .1
            resultset.append(list(current_episode_trajectories[i][1:]) + [current_reward, 0])

    resultset.append(list(current_episode_trajectories[NUM_EPISODE_HORIZON_CONTROLLED-1][1:]) + [current_episode_trajectories[-1][0], 0])
    return resultset


def building_condition(key, position, environment):
    if key == 'w':
        return environment.findReduceRessource('wood', position, 6, reduce=False)
    if key == 'k':
        return len(np.where(environment.reduceArrayToRadius(environment.owned_terrain,
                                                            position, 3) == 0)) > 0

    return True

def get_pseudo_random_position(environment, key, complete_random_threshold=0.):
    possible = np.where(environment.get_owned_terrain() == 1)
    cell = None

    complete_random = random.random()
    # TODO: take most-favorable position out of 20?
    for _ in range(20):
        position = random.randint(0, len(possible[0]) - 1)
        x, y = possible[0][position], possible[1][position]
        cell = (x, y)

        if environment.check_coordinates_buildable(cell) and (complete_random < complete_random_threshold or
                                                              building_condition(key, cell, environment)):
            break
    return cell

def get_current_timestring():
    named_tuple = time.localtime()  # get struct_time
    time_string = time.strftime("%Y%m%d_%H_%M", named_tuple)
    return time_string


def load_environment_data():
    with open(path_append("training/models/ra.pckl"), 'rb') as hd:
        ls_ra = pickle.load(hd)

    with open(path_append("training/models/occ.pckl"), 'rb') as hd:
        ls_occ = pickle.load(hd)

    with open(path_append("training/models/building.pckl"), 'rb') as hd:
        building_pos = pickle.load(hd)

    return [ls_ra, ls_occ, building_pos]


def instanciate_environment(ls_ra, ls_occ, building_pos):
    s = Environment()
    c = Control(s, copy.deepcopy(ls_ra), copy.deepcopy(ls_occ), copy.deepcopy(building_pos))

    return s, c


def save_everything(m_action, m_coords, top_10_games, state, prefix=''):

    named_tuple = time.localtime()  # get struct_time
    time_string = time.strftime("%Y%m%d_%H_%M", named_tuple)
    m_action.save("models/%s_%s_action.h5"%(time_string, prefix))
    m_coords.save("models/%s_%s_coords.h5"%(time_string,prefix))
    with open("models/%s_%s_top10.pckl"%(time_string,prefix), 'wb') as hd:
        pickle.dump(top_10_games, hd)
    from matplotlib import pyplot as plt
    plt.imsave("models/%s_%s_state.png"%(time_string,prefix), state.get_landscape_occupation())
    with open("models/%s_%s_state.pckl"%(time_string,prefix), 'wb') as hd:
        pickle.dump(state, hd)

def load_state_top10(time_string):

    with open("models/%s_top10.pckl"%(time_string), 'rb') as hd:
        top_10_games = pickle.load(hd)

    return top_10_games

def load_state_models(time_string):

    action = tf.keras.models.load_model("models/%s_action.h5"%(time_string))
    coords = tf.keras.models.load_model("models/%s_coords.h5"%(time_string))
    return action, coords