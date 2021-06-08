import tensorflow as tf
import time
import pickle
import copy

from control import Control
from state import State


ACTION_SPACE = 5
ENVIRONMENT_DIMENSION = (50, 50)

NUM_EPISODES = 10
NUM_EPISODE_HORIZON_OBSERVED = 30
NUM_EPISODE_HORIZON_CONTROLLED = 15


# ## Constants:
# RL Constants:
DISCOUNT               = 0.99
REPLAY_MEMORY_SIZE     = 3_000   # How many last steps to keep for model training
MIN_REPLAY_MEMORY_SIZE = 1_000   # Minimum number of steps in a memory to start training
UPDATE_TARGET_EVERY    = 20      # Terminal states (end of episodes)
MIN_REWARD             = 1000    # For model save
SAVE_MODEL_EVERY       = 1000    # Episodes
SHOW_EVERY             = 20      # Episodes
EPISODES               = 10_000  # Number of episodes
#  Stats settings
AGGREGATE_STATS_EVERY = 20  # episodes
SHOW_PREVIEW          = False


def load_environment_data():
    with open("ra.pckl", 'rb') as hd:
        ls_ra = pickle.load(hd)

    with open("occ.pckl" , 'rb') as hd:
        ls_occ = pickle.load(hd)

    with open("building.pckl" , 'rb') as hd:
        building_pos = pickle.load(hd)

    return [ls_ra, ls_occ, building_pos]


def instanciate_environment(ls_ra, ls_occ, building_pos):
    s = State()
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