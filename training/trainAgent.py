from training.agents.DQNAgent import DQNAgent
from training.misc.model_misc import *
from training.agents.DiscoverAgent import DiscoverAgent
from training.misc.training_misc import *


def get_extended_score(environment):
    return 150 + environment.get_score() + np.sum(list(environment.produced_dict.values()))*5 + np.sum(environment.get_owned_terrain())/5

LOAD_MODEL = '' #'20210619_13_03'
DO_TRAIN = True
VERBOSE_OUTPUT = 10

epsilon_greedy = .15
current_num_episodes = 1000*100 # NUM_EPISODES

#TODO: save each 1k steps
#   print each 10 epochs a "real" trajectory without epsilon

if __name__ == '__main__':

    environment_data = load_environment_data()

    if not DO_TRAIN:
        epsilon_greedy = 0.
        current_num_episodes = 1

    #dqn_agent = DQNAgent(discount_factor=0.9, reward_lookahead=1, epsilon_greedy=epsilon_greedy)
    #dqn_agent.load_replay_memory('training/models/random/20210619_22_21_replay_memory.pckl')
    #agent = dqn_agent

    discover_agent = DiscoverAgent(discount_factor=0.9, reward_lookahead=1, epsilon_greedy=epsilon_greedy)
    agent = discover_agent


    if LOAD_MODEL:
        agent.load(LOAD_MODEL)

    for game_nr in range(current_num_episodes):
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

        if DO_TRAIN:
            agent.train()
            if game_nr % 100000 == 999:
                agent.save(game_nr)

    print(agent)

    if DO_TRAIN:
        agent.save()

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