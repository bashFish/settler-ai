
from tensorflow.python.keras.utils import losses_utils

from control import Control
from misc import parse_buildings
from environment import Environment

from model_misc import *
from game_misc import *
from training.DQNAgent import DQNAgent, RandomAgent
from training_misc import *




if __name__ == '__main__':

    environment_data = load_environment_data()

    agent = DQNAgent(discount_factor=0.9, reward_lookahead=5)

    for game_nr in range(NUM_EPISODES):
        print("\tgame %s" % (game_nr))

        #TODO: merge control and env?
        environment, control = instanciate_environment(*environment_data)

        game_move_nr = 0
        for _ in control.yieldloop():
            game_move_nr += 1

            action = None
            if game_move_nr < NUM_EPISODE_HORIZON_CONTROLLED:

                action = agent.choose_action(extract_state(environment))

                if action:
                    environment.add_game_event(action)

            if game_move_nr >= NUM_EPISODE_HORIZON_OBSERVED:
                break
            elif game_move_nr > 1:
                agent.append_trajectory((environment.get_score(),
                                         *last_state_action,
                                         extract_state(environment)))
            last_state_action = [extract_state(environment), action]

        agent.end_episode()
        agent.train()

"""
1- Initialize replay memory capacity.
2- Initialize the policy network with random weights.
3- Clone the policy network, and call it the target network (target_model).
4- For each episode:
    1. Initialize the starting environment.
    2. For each time step:
        1- Select an action.
            - Via exploration or exploitation, which depends on epsilon.
        2- Execute selected action in an emulator (the environment).
        3- Observe reward and next environment.
        4- Store experience in replay memory.
        5- Sample random batch from replay memory.
        6- Preprocess states from batch (normalization).
        7- Pass batch of preprocessed states to policy network.
        8- Calculate loss between output Q-values and target Q-values.
            - Requires a pass to the target network for the next environment
        9- Gradient descent updates weights in the policy network to minimize loss.
            - After x time steps, weights in the target network are updated to the weights in the policy network.
"""