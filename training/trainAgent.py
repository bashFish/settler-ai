import copy

from tensorflow.python.keras.utils import losses_utils

from control import Control
from misc import parse_buildings
from state import State

from model_misc import *
from game_misc import *
from training_misc import *


num_games = 1000
observed_moves_per_game = 20
moves_per_game = 6

buildings, key_to_building, objectid_to_building = parse_buildings()
rows, cols = 50, 50

all_keys = list(key_to_building.keys())
all_keys.extend(['-']) # for now don't demolish building/ end game  ['d', 'q', '-']


if __name__ == '__main__':

    m_action = model_action()
    m_coords = model_coordinates()

    with open("ra.pckl", 'rb') as hd:
        ls_ra = pickle.load(hd)

    with open("occ.pckl" , 'rb') as hd:
        ls_occ = pickle.load(hd)

    with open("building.pckl" , 'rb') as hd:
        building_pos = pickle.load(hd)

    for game_nr in range(num_games):
        print("\tgame %s" % (game_nr))

        s = State()
        g = Control(s, copy.deepcopy(ls_ra), copy.deepcopy(ls_occ), copy.deepcopy(building_pos))


"""

        # Creating the dense layers:
        for d in dense_list:
            _ = Dense(units=d, activation='relu')(_)
        # The output layer has 5 nodes (one node per action)
        output = Dense(units=self.env.ACTION_SPACE_SIZE,
                          activation='linear', name='output')(_)
        
        # Put it all together:
        model = Model(inputs=input_layer, outputs=[output])
        model.compile(optimizer=Adam(lr=0.001),
                      loss={'output': 'mse'},
                      metrics={'output': 'accuracy'})
                  
                  
                  
1- Initialize replay memory capacity.
2- Initialize the policy network with random weights.
3- Clone the policy network, and call it the target network (target_model).
4- For each episode:
    1. Initialize the starting state.
    2. For each time step:
        1- Select an action.
            - Via exploration or exploitation, which depends on epsilon.
        2- Execute selected action in an emulator (the environment).
        3- Observe reward and next state.
        4- Store experience in replay memory.
        5- Sample random batch from replay memory.
        6- Preprocess states from batch (normalization).
        7- Pass batch of preprocessed states to policy network.
        8- Calculate loss between output Q-values and target Q-values.
            - Requires a pass to the target network for the next state
        9- Gradient descent updates weights in the policy network to minimize loss.
            - After x time steps, weights in the target network are updated to the weights in the policy network.
"""