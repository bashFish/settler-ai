from training.misc.model_misc import *
from training.misc.training_misc import *


VERBOSE_OUTPUT = 10


def get_extended_score(environment):
    return 150 + environment.get_score() + np.sum(list(environment.produced_dict.values()))*5 + np.sum(environment.get_owned_terrain())/5


def train_loop(agent, num_episodes, savepoint_steps = 0):

    environment_data = load_environment_data()

    for game_nr in range(num_episodes):
        print("\tgame %s" % (game_nr))

        #TODO: merge control and env?
        environment, control = instanciate_environment(*environment_data)

        game_move_nr = 0
        for _ in control.yieldloop():
            game_move_nr += 1

            action = None
            if game_move_nr < NUM_EPISODE_HORIZON_CONTROLLED:

                action = agent.choose_action(environment, (game_nr % VERBOSE_OUTPUT) == 0)

                if action:
                    environment.add_game_event(*action)

            if game_move_nr >= NUM_EPISODE_HORIZON_OBSERVED:
                break
            elif game_move_nr > 1:
                agent.append_trajectory((get_extended_score(environment),
                                         *last_state_action,
                                         extract_state(environment)))
            last_state_action = [extract_state(environment), action]

        agent.end_episode((game_nr % VERBOSE_OUTPUT) == 0)

        agent.train()
        if savepoint_steps and game_nr % savepoint_steps == (savepoint_steps-1):
            agent.save(game_nr)

    print(agent)

    agent.save(game_nr)

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