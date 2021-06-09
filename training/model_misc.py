import tensorflow as tf
import numpy as np

from building.sawmill import Sawmill
from building.woodcutter import Woodcutter


def state_representation(state):
    #TODO: later include
    #   state.availableCarrier,
    #   state.settler_score_penalty]
    return list(state.state_dict.values()) + np.sum(state.owned_terrain) + list(state.produced_dict.values()) + \
           [sum([1 for s in state.buildings if s == Sawmill and s.finished == True]),
            sum([1 for s in state.buildings if s == Sawmill and s.finished == False]),
            sum([1 for s in state.buildings if s == Woodcutter and s.finished == True]),
            sum([1 for s in state.buildings if s == Woodcutter and s.finished == False])]

def statemap_to_model_input(state):
    # state.owned_terrain           # 0/1
    # state.landscape_occupation    # 8 is wood, woodcutter: +/- 3, barack: +/- 6, other: occupied
    return np.stack([state.owned_terrain, state.landscape_occupation != 0, state.landscape_occupation == 8,
                     np.abs(state.landscape_occupation) == 3, np.abs(state.landscape_occupation) == 6])


def model_action():
    map = tf.keras.models.Sequential()
    map.add(tf.keras.Input(shape=(50,50,5)))
    map.add(tf.keras.layers.Conv2D(32, (3, 3), padding="same", activation='relu'))
    map.add(tf.keras.layers.Dense(50, activation='relu'))
    map.add(tf.keras.layers.Dense(50, activation='relu'))

    dictionary = tf.keras.models.Sequential()
    dictionary.add(tf.keras.Input(shape=(12+3)))
    dictionary.add(tf.keras.layers.Dense(50, activation='relu'))

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Concatenate()([map, dictionary]))
    model.add(tf.keras.layers.Dense(150, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))

    #TODO: remove should be handled somewhat different
    model.add(tf.keras.layers.Dense(5, activation='linear',
        kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4),
        bias_regularizer=tf.keras.regularizers.l2(1e-4),
        activity_regularizer=tf.keras.regularizers.l1(1e-3)))

    #model.summary()
    return model


#TODO: one for each building?
#TODO: could also insert map in multiple layers (wood/ woodcutter/ ...) = embedding
#TODO: use deconvolutional -> generate heat map here?
def model_coordinates():
    map = tf.keras.models.Sequential()
    map.add(tf.keras.Input(shape=(50,50,5)))
    map.add(tf.keras.layers.Conv2D(32, (3, 3), padding="same", activation='relu'))
    map.add(tf.keras.layers.Conv2D(32, (3, 3), padding="same", activation='relu'))
    map.add(tf.keras.layers.Dropout(.1))
    map.add(tf.keras.layers.Dense(50, activation='relu'))
    map.add(tf.keras.layers.Dense(50, activation='relu'))
    map.add(tf.keras.layers.Dense(2)) # < must be in 0,50

    return map


def prediction_to_coords(preds):
    coords = preds*10
    cell = (int(min(abs(coords[0]), 49)), int(min(abs(coords[1]) , 49)))
    return cell