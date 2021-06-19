import copy
import pickle
import time

from tensorflow.python.keras.utils import losses_utils

from control import Control
from events import GameEvent
from misc import parse_buildings
from state import State
import csv

from model_misc import *
from game_misc import *
from training_misc import *


num_games = 1000
observed_moves_per_game = 20
moves_per_game = 6


buildings, key_to_building, objectid_to_building = parse_buildings()
rows, cols = 50, 50

# top 10 moves of top 10 games
top_10_games = [(-100000, [])]*10

all_keys = list(key_to_building.keys())
all_keys.extend(['-']) # for now don't demolish building/ end game  ['d', 'q', '-']


if __name__ == '__main__':

    time_str = '' # trained for 5k moves with 80% random moves

    m_action = model_action()
    m_coords = model_coordinates()

    if time_str:
        load_state_top10(time_str)
        m_action, m_coords = load_state_models(time_str)

    loss_function = tf.keras.losses.Huber(delta=1.0, reduction=losses_utils.ReductionV2.AUTO)
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.00025, clipnorm=.5)

    with open("../training/models/ra.pckl", 'rb') as hd:
        ls_ra = pickle.load(hd)

    with open("../training/models/occ.pckl", 'rb') as hd:
        ls_occ = pickle.load(hd)

    with open("../training/models/building.pckl", 'rb') as hd:
        building_pos = pickle.load(hd)

    for j in range(num_games):
        print("\tgame %s" % (j))
        s = State()
        g = Control(s, copy.deepcopy(ls_ra), copy.deepcopy(ls_occ), copy.deepcopy(building_pos))

        state_history = []
        action_history = []
        action_input = []
        coord_input = []
        score_history = []
        movetaker = 0

        i = 1
        if top_10_games[0][0] < 0:
            choice = 0.1
        else:
            choice = random.random()
        for r in g.yieldloop():
            print("\t %s \t %s \t %s " % (j, i, s.get_score()))
            predict_key, coords = '-', None
            predict_key_position = None
            moveTaken = False


            if i < 11:
                # TODO: Use epsilon-greedy for exploration
                if top_10_games[-1][0] > 0:
                    if choice > .95:
                        predict_key, _, coords = top_10_games[-1][1][i]
                        print("best %s %s"%(predict_key, coords))
                        moveTaken = True
                        movetaker = 1
                    elif choice > .70:
                        predict_key, coords = get_best_player_move_randomized(key_to_building, top_10_games, s, i)
                        print("random %s %s"%(predict_key, coords))
                        moveTaken = True
                        movetaker = 2

                if predict_key is not None and predict_key_position is None:
                    for ijk in range(5):
                        if all_keys[ijk] == predict_key:
                            building = tf.one_hot(ijk, 5)
                            predict_key_position = ijk

                if not moveTaken:
                    prediction = m_action.predict(state_representation(s))

                    #print(prediction)
                    move = prediction[0][10:]
                    predict_key_position = np.argmax(move)
                    predict_key = all_keys[predict_key_position]
                    building = tf.one_hot(predict_key_position, 5)
                    coords = None

                    if predict_key != '-':
                        prediction_2 = m_coords.predict(state_representation_vector_2(s, old_gambled_states, building))
                        coords = prediction_to_coords(prediction_2[0])

                if predict_key != '-':
                    while not s.check_coordinates_buildable(coords):
                        possible = np.where(s.get_owned_terrain() == 1)
                        position = random.randint(0, len(possible[0]) - 1)
                        coords = (possible[0][position],possible[1][position])

                    s.add_game_event(GameEvent.CONSTRUCT_BUILDING, (coords, key_to_building[predict_key]))

            print(" taken %s %s"%(predict_key, coords))

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
                updated_q_values = (np.array(score_history[35:45])-np.array(score_history[:10]))

                with tf.GradientTape() as tape:
                    tape.watch(m_action.trainable_variables)
                    q_values = m_action(np.array([action_input[:10]]))
                    q_action = tf.reduce_sum(tf.multiply(q_values[:, :, 10:], move_matrices),axis=2)
                    #TODO: could be trained differently / wo multiply but abs distance:
                    #    (move_taken_in_matrix [0,1,0,0,0] - this_output) * loss

                    loss = loss_function(updated_q_values, q_action)
                    grads = tape.gradient(loss, m_action.trainable_variables)

                optimizer.apply_gradients(zip(grads, m_action.trainable_variables))

                current_coords_in = []
                current_updated_q = []
                target_coords = []
                for histi, histk in enumerate(action_history[:10]):
                    if coord_input[histi] is not None:
                        current_coords_in.append(coord_input[histi])
                        current_updated_q.append(score_history[histi+30]-score_history[histi])
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
                if lowest[0] < score_history[-1] and score_history[-1] not in [sc[0] for sc in top_10_games]:
                    del top_10_games[lowest[1]]
                    top_10_games.append((score_history[-1], action_history[:11]))
                    top_10_games.sort()

                with open('models/training_score_%s.csv'%(time_str), 'w', newline='') as csvfile:

                    csvwriter = csv.writer(csvfile, delimiter=';')
                    csvwriter.writerow([j, movetaker, score_history[-1], action_history[:10]])

                state_history = [] #state_history[-20:]
                action_history = [] #action_history[-20:]
                action_input = [] #action_input[-20:]
                coord_input = [] #coord_input[-20:]
                score_history = [] #score_history[-20:]

            i += 1
            #time.sleep(1)
            if i > 51: #20*moves_per_game+1:
                if j % 4000 == 0:
                    save_everything(m_action, m_coords, top_10_games,s,str(j))
                    print(top_10_games)
                break

        #print("Final score: %s/ %s" % (s.get_score(), s.get_ticks()))
    save_everything(m_action,m_coords,top_10_games, s, 'final')

