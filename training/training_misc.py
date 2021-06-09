import tensorflow as tf
import time
import pickle
import copy


from control import Control
from environment import Environment


ACTION_SPACE = 5
ENVIRONMENT_DIMENSION = (50, 50)

TRAIN_MODEL_NAME = 'first_shot'
TRAIN_MINIBATCH_SIZE = 64
TRAIN_MIN_REPLAY_MEMORY_SIZE = 100
TRAIN_MEMORY_SIZE = 1000
TRAIN_UPDATE_TARGET_STEPS = 25
NUM_EPISODES = 100
NUM_EPISODE_HORIZON_OBSERVED = 30
NUM_EPISODE_HORIZON_CONTROLLED = 15





def load_environment_data():
    with open("ra.pckl", 'rb') as hd:
        ls_ra = pickle.load(hd)

    with open("occ.pckl" , 'rb') as hd:
        ls_occ = pickle.load(hd)

    with open("building.pckl" , 'rb') as hd:
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