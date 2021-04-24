import copy
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


buildings, key_to_building, objectid_to_building = parse_buildings()
rows, cols = 50, 50

all_keys = list(key_to_building.keys())
all_keys.extend(['d', 'q', '-'])

num_games = 10000
moves_per_game = 10  # it's approximated moves! actually: 10*20=200 ticks! # can't be just one, othw always starts with barack


#TODO: find/ store top game moves!
#           train towards that one
#   eg: move[1] sawmill [pos1 pos2] or sawmill -> [pos1/2, pos3/4,...], randomly pick out of
#      building prediciton at move 1 sawmill ->  second network trained towards pos1/2
#   best game strategy: sawmill,  woodcutter -> predict that
#                   ALREADY predict multiple moves in the begining?
#
#   -> 30% exchange a move, then 30% exchange a coordinate

# open research problems AI
#   - NLP
#   - auto-mapping and more precise output (no one-hot encode/ hand-crafted lstm etc.)
#   -

# TODO : abort game when gameover!! -> penalty on all moves that led there.
# TODO: 1) invalid move -> penalty! auch bei action (eg keine bretter mehr da)
#       2)   mehr als 5 ticks in vorraus schauen! vielleicht in 5 und in 10! (erst da wird produktion anfangen)

# 0 0 TODO: owned land doch schon mitgeben?
#           heatmap, nicht 2 koordinaten ausgeben!(?)
#0) FIRST THING TO EXCHANGE: internal state needs to be trained separatedly!

#1) learn valid moves
#2) learn basic objectives: wood->cutter around/ wood -> sawmill -> plank/ barack extends
#3) learn strategies: all needs planks -> need pipeline/  -> find all wood + reach all area = top score
#4) elements should be exchangeable -> don't want to retrain everything just cuz i changed a building

#5) in my mind, i already have a map/target state, that gets refined every now and then.
#       so have a network learning that one, and then one ordering the needed moves.

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
    model.add(tf.keras.Input(shape=(50*50+11+3+10*10)))
    model.add(tf.keras.layers.Dense(350, activation='relu'))
    model.add(tf.keras.layers.Dense(250, activation='relu'))
    model.add(tf.keras.layers.Dense(150, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    #TODO: remove should be handled somewhat different
    model.add(tf.keras.layers.Dense(5+10)) # 7 moves possible, 10 = new state
    print("in/out : %s %s" %(50*50+5+3+10*10, 5+10))
    model.summary()
    return model

def model_coordinates(): #TODO: use convolutional -> generate heat map here?
    model = tf.keras.models.Sequential()
    model.add(tf.keras.Input(shape=(50*50+10*10+5)))
    model.add(tf.keras.layers.Dense(250, activation='relu'))
    model.add(tf.keras.layers.Dense(150, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    model.add(tf.keras.layers.Dense(20, activation='relu'))
    model.add(tf.keras.layers.Dense(2)) # < must be in 0,50
    model.summary()
    print("input: %s" %(50*50+10*10+15))
    return model

all_keys_model = all_keys[:]
all_keys_model.remove('q')
all_keys_model.remove('d')
print(len(all_keys_model))

#First: train for games that last only 150 ticks. should resolve in some ai (that doesnt abort immediate :D)
#LATER: let them battle against each other


#TODO: maybe ai needs really random moves to find buildable locations?
def generate_random_valid_action(state):
    #TODO: start directly with search tree! only valid moves for starters (?)
    #key = random.choice(all_keys)

    category = random.random()
    coordinate = None

    #print("added action: %s %s" %(key, cell))
    if category < .05 and False: #key == 'd': #TODO: not yet delete!
        b = random.choice(state.buildings)
        cell = (b.coordinate)
        state.add_game_event(GameEvent.DROP, cell)
        key = 'd'

    #elif key == 'q':
    #    state.add_game_event(GameEvent.END_GAME)
    elif category > .6: #key != '-':
        key = random.choice(list(key_to_building.keys()))
        possible = np.where(state.get_owned_terrain() == 1)
        position = random.randint(0, len(possible[0])-1)
        x, y = possible[0][position], possible[1][position]
        cell = (x, y)
    else:
        key = '-'
        cell = None

    return key, cell

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
            len([s for s in state.buildings if s == Sawmill]),
            len([s for s in state.buildings if s == Woodcutter]),
            state.availableCarrier,
            state.tick,
            state.settler_score_penalty] #, state.get_score()]

def state_representation_vector(state,old_states):

    cur = state_representation(state)
    result = np.array([np.hstack([cur[0].reshape(-1),np.array(old_states).reshape(-1),np.array(cur[1]),np.array(cur[2:])]).astype(np.int)])
    #print(result.shape)
    return result

def state_representation_vector_2(state,old_states,building):

    cur = state_representation(state)
    result = np.array([np.hstack([cur[0].reshape(-1),np.array(old_states).reshape(-1),building]).astype(np.int)])
    #print(result.shape)
    return result

# learn each valid move
# - eg construction works only within range, delete only on buildings
# - woodcutter only produces wood if around wood, sawmill only planks if wood available
# - carrier needs to be there
# - need to expand area
# - "more planks" -> "need sawmill, but also more wood"
# - detect areas on map to be used eventually, eg with wood etc

"""
def prediction_to_coords(preds):
    coords = preds*10
    cell = (int(min(round(abs(coords[0]), -1) / 10, 49)), int(min(round(abs(coords[1]), -1) / 10, 49)))
    return cell
"""

def prediction_to_coords(preds):
    coords = preds*10
    cell = (int(min(abs(coords[0]) , 49)), int(min(abs(coords[1]) , 49)))
    return cell

# top 10 moves of top 10 games
top_10_games = [(-100000,[])]*10
top_building_coords = {}

#TODO: this is going to be replaced by a target player!
# let ais play against each other
# this player does not generalize to other maps!
def get_best_player_move_randomized(state, move):
    #highest = max((sc[0], it) for it, sc in enumerate(top_10_games))
    highest = top_10_games[-1]
    if random.random() > .9 or highest[0] < 0:   # 5 % total random moves
        key, cell = generate_random_valid_action(state)
    else:
        current = -1
        while current > -8 and top_10_games[current-1][0] > 0 and random.random() > .7:
            current -= 1
        key,_, cell = top_10_games[current][1][move]

    return key, cell

#TODO: copied configs!
if __name__ == '__main__':

    m_action = model_action()
    m_coords = model_coordinates()

    loss_function = tf.keras.losses.Huber(delta=1.0, reduction=losses_utils.ReductionV2.AUTO)
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)

    for j in range(num_games):
        print("\t %s" % (j))
        s = State()
        g = Control(s)
        old_gambled_states = [np.zeros(10)] * 10

        state_history = []
        action_history = []
        action_input = []
        coord_input = []
        score_history = []

        i = 1
        for r in g.yieldloop():
            print("\t %s \t %s \t %s %s" % (j, i, s.get_score(), s.get_state_dict()))
            predict_key, coords = '-', None

            if i < 10:
                # TODO: Use epsilon-greedy for exploration
                if random.random() > 0.2: # 80% best player / random moves
                    predict_key, coords = get_best_player_move_randomized(s, i)
                    print("random %s %s"%(predict_key, coords))
                    if predict_key != '-':
                        s.add_game_event(GameEvent.CONSTRUCT_BUILDING, (coords, key_to_building[predict_key]))

                    for ijk in range(5):
                        if all_keys_model[ijk] == predict_key:
                            building = tf.one_hot(ijk, 5)
                            predict_key_position = ijk

                else:
                    prediction = m_action.predict(state_representation_vector(s, old_gambled_states))

                    old_gambled_states.append(prediction[0][:10])
                    del old_gambled_states[0]

                    move = prediction[0][10:]
                    predict_key_position = np.argmax(move)
                    predict_key = all_keys_model[predict_key_position]
                    building = tf.one_hot(predict_key_position, 5)
                    coords = None

                    if predict_key != '-':
                        prediction_2 = m_coords.predict(state_representation_vector_2(s, old_gambled_states, building))
                        coords = prediction_to_coords(prediction_2[0])

                        while not s.check_coordinates_buildable(coords):
                            possible = np.where(s.get_owned_terrain() == 1)
                            position = random.randint(0, len(possible[0]) - 1)
                            coords = (possible[0][position],possible[1][position])

                        s.add_game_event(GameEvent.CONSTRUCT_BUILDING, (coords, key_to_building[predict_key]))

                    print(" predicted %s %s"%(predict_key, coords))

            action_input.append(state_representation_vector(s, old_gambled_states)[0])
            if predict_key and predict_key != '-':
                coord_input.append(state_representation_vector_2(s, old_gambled_states, building))
            else:
                coord_input.append(None)
            action_history.append((predict_key, predict_key_position, coords))
            score_history.append(s.get_score())

            # train step
            if i % 50 == 0:
                move_matrices = tf.one_hot([c[1] for c in action_history[:10]], 5)
                updated_q_values = np.array(score_history[5:15])-np.array(score_history[:10])+(np.array(score_history[35:45])-np.array(score_history[:10]))*2

                with tf.GradientTape() as tape:
                    tape.watch(m_action.trainable_variables)
                    q_values = m_action(np.array([action_input[:10]]))
                    q_action = tf.reduce_sum(tf.multiply(q_values[:, :, 10:], move_matrices),axis=2) #TODO: could be trained differently / wo multiply but abs distance

                    loss = loss_function(updated_q_values, q_action)
                    grads = tape.gradient(loss, m_action.trainable_variables)

                optimizer.apply_gradients(zip(grads, m_action.trainable_variables))

                current_coords_in = []
                current_updated_q = []
                target_coords = []
                for histi, histk in enumerate(action_history[:10]):
                    if coord_input[histi] is not None:
                        current_coords_in.append(coord_input[histi])
                        current_updated_q.append(score_history[histi+10]-score_history[histi]+(score_history[histi+30]-score_history[histi])*2)
                        target_coords.append(action_history[histi][2])

                if len(current_coords_in):
                    with tf.GradientTape() as tape:

                        tape.watch(m_coords.trainable_variables)
                        q_values_coords = m_coords(np.array(current_coords_in))[:,0,:]
                        # q_action_coords = tf.reduce_sum(tf.multiply(q_values_coords[:, :, 10:], move_matrices),axis=2)
                        #if coord

                        for ijf, coo in enumerate(q_values_coords):
                            curcod = prediction_to_coords(coo.numpy())
                            x,y = target_coords[ijf]
                            current_updated_q[ijf] -= abs(coo[0]*10-x) + abs(coo[1]*10-y)

                        #coords = (q_values_coords)
                        #print(coords, s.check_coordinates_buildable(coords))
                        #print(current_updated_q, q_values_coords[:,0])
                        loss = loss_function(current_updated_q, q_values_coords[:,0] + q_values_coords[:,1])
                        grads2 = tape.gradient(loss, m_coords.trainable_variables)

                    optimizer.apply_gradients(zip(grads2, m_coords.trainable_variables))

                lowest = min((sc[0],it) for it, sc in enumerate(top_10_games))
                if lowest[0] < score_history[-1]:
                    del top_10_games[lowest[1]]
                    top_10_games.append((score_history[-1], action_history[:10]))
                    top_10_games.sort()


                state_history = [] #state_history[-20:]
                action_history = [] #action_history[-20:]
                action_input = [] #action_input[-20:]
                coord_input = [] #coord_input[-20:]
                score_history = [] #score_history[-20:]

                break

            i += 1
            #time.sleep(1)
            #if i > 51: #20*moves_per_game+1:
            #    break


        #print("Final score: %s/ %s" % (s.get_score(), s.get_ticks()))
    named_tuple = time.localtime()  # get struct_time
    time_string = time.strftime("%Y%m%d_%H_%M", named_tuple)

    m_action.save("models/action_%s.h5"%(time_string))
    m_coords.save("models/coords_%s.h5"%(time_string))
