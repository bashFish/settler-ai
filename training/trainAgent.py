
from tensorflow.python.keras.utils import losses_utils

from control import Control
from misc import parse_buildings
from state import State

from model_misc import *
from game_misc import *
from training.DQNAgent import DQNAgent, RandomAgent
from training_misc import *





if __name__ == '__main__':

    environment_data = load_environment_data()

    random_agent = RandomAgent(0.8)
    agent = DQNAgent()

    for game_nr in range(NUM_EPISODES):
        print("\tgame %s" % (game_nr))

        state, control = instanciate_environment(*environment_data)

        game_move_nr = 0
        for _ in control.yieldloop():
            game_move_nr += 1

            if game_move_nr < NUM_EPISODE_HORIZON_CONTROLLED:

                action = agent.get_action(state)

                if action:
                    state.add_game_event(action)

            if game_move_nr >= NUM_EPISODE_HORIZON_OBSERVED:
                break
"""
                  
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