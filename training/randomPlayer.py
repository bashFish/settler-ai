import time

import numpy as np

from control import Control
from events import GameEvent
from misc import parse_buildings
from state import State
import random


buildings, key_to_building, objectid_to_building = parse_buildings()
rows, cols = 50, 50

all_keys = list(key_to_building.keys())
all_keys.extend(['d', 'q', '-'])

# open research problems AI
#   - NLP
#   - auto-mapping and more precise output (no one-hot encode/ hand-crafted lstm etc.)
#   -


#1) learn valid moves
#2) learn basic objectives: wood->cutter around/ wood -> sawmill -> plank/ barack extends
#3) learn strategies: all needs planks -> need pipeline/  -> find all wood + reach all area = top score
#4) elements should be exchangeable -> don't want to retrain everything just cuz i changed a building

# HANDCRAFTED EXPERT MODELS PERFORM WORSE!
# NEED AN EVOLUTIONARY ALGORITHM UNDERNEATH THAT CONSTRUCT AND FINDS ITS PATH
#
# First try one network!
# Later: one network per move and one per strategy and find a path thru the networks "compiling" a move.
#            get much more efficient!
#
#
# INPUT:
# - current state - complete
# - last 15 states - encoded    << should be lstm lateron?
# OUTPUT:
# - code
# - current move decision       << one hot or not?

#TODO: try an all-in-one-model and all-split-model as well!

import tensorflow as tf

def model_action():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.Input(shape=(50*50+5+4+10*10,)))
    model.add(tf.keras.layers.Dense(250, activation='relu'))
    model.add(tf.keras.layers.Dense(150, activation='relu'))
    model.add(tf.keras.layers.Dense(250, activation='relu'))
    model.add(tf.keras.layers.Dense(150, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    #TODO: remove should be handled somewhat different
    model.add(tf.keras.layers.Dense(7+10)) # 7 moves possible, 10 = new state
    print("in/out : %s %s" %(50*50+5+4+10*10, 7+10))
    model.summary()
    return model

def model_coordinates(): #TODO: use convolutional -> generate heat map here?
    model = tf.keras.models.Sequential()
    model.add(tf.keras.Input(shape=(50*50+10*10+17,)))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    model.add(tf.keras.layers.Dense(20, activation='relu'))
    model.add(tf.keras.layers.Dense(2)) # < must be in 0,50
    model.summary()
    print("input: %s" %(50*50+10*10+17))
    return model

all_keys_model = all_keys[:]
all_keys_model.remove('q')
all_keys_model.remove('d')
print(len(all_keys_model))

#First: train for games that last only 150 ticks. should resolve in some ai (that doesnt abort immediate :D)
#LATER: let them battle against each other


def enqueue_random_action(state):
    #TODO: start directly with search tree! only valid moves for starters (?)
    key = random.choice(all_keys)
    x, y = random.randint(0,49), random.randint(0,49)
    cell = (x,y)

    print("added action: %s %s" %(key, cell))
    if key == 'd':
        state.add_game_event(GameEvent.DROP, cell)
    elif key == 'q':
        state.add_game_event(GameEvent.END_GAME)
    elif key != '-':
        state.add_game_event(GameEvent.CONSTRUCT_BUILDING, (cell, key_to_building[key]))
    # othw: do nothing/ wait


#TODO: construction needs to be more clear
# # # # -> currently it can be forgotten what building is being constructed (?)
# # # #    unless mystical hidden state keeps it
def state_representation(state):
    #state.owned_terrain, can be inherited from map
    #state.buildings, # can be inherited from occupation map
    return [state.landscape_occupation,
            list(state.state_dict.values()),
            state.availableCarrier,
            state.tick,
            state.settler_score_penalty, state.get_score()]

def state_representation_vector(state,old_states):

    cur = state_representation(state)
    result = np.array([np.hstack([cur[0].reshape(-1),np.array(old_states).reshape(-1),np.array(cur[1]),np.array(cur[2:])]).astype(np.int)])
    #print(result.shape)
    return result

def state_representation_vector_2(state,old_states,model1_out):

    cur = state_representation(state)
    result = np.array([np.hstack([cur[0].reshape(-1),np.array(old_states).reshape(-1),model1_out[0]]).astype(np.int)])
    #print(result.shape)
    return result

# learn each valid move
# - eg construction works only within range, delete only on buildings
# - woodcutter only produces wood if around wood, sawmill only planks if wood available
# - carrier needs to be there
# - need to expand area
# - "more planks" -> "need sawmill, but also more wood"
# - detect areas on map to be used eventually, eg with wood etc

#TODO: copied configs!
if __name__ == '__main__':

    m_action = model_action()
    m_coords = model_coordinates()

    s = State()
    g = Control(s)
    old_gambled_states = [np.zeros(10)] * 10

    i = 0
    for r in g.yieldloop():
        enqueue_random_action(s)

        prediction = m_action.predict(state_representation_vector(s, old_gambled_states))
        prediction_2 = m_coords.predict(state_representation_vector_2(s, old_gambled_states, prediction))

        old_gambled_states.append(prediction[0][:10])
        del old_gambled_states[0]

        move = prediction[0][10:]
        coords = prediction_2[0]
        predict_key_position = np.argmax(move)

        print(move, coords)
        print(predict_key_position)
        print(all_keys_model[predict_key_position])

        time.sleep(1)
        i += 1
        if i > 2:
            break


    print("Final score: %s/ %s" % (s.get_score(), s.get_ticks()))