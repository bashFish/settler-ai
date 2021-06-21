from events import GameEvent
from training.agents.DiscoverAgent import DiscoverAgent
from training.misc.model_misc import *
from training.misc.training_misc import *
from training.trainAgent import get_extended_score

discover_agent = DiscoverAgent(discount_factor=0.9, reward_lookahead=1, epsilon_greedy=.1)
agent = discover_agent

#episode = [( ((28, 25), 'Barack')), None, ( ((19, 21), 'Woodcutter')), None, ( ((23, 23), 'Sawmill')), ( ((18, 18), 'Sawmill')), ( ((26, 23), 'Sawmill')), ( ((24, 23), 'Sawmill')), ( ((20, 20), 'Sawmill')), ( ((26, 28), 'Sawmill')), ( ((29, 27), 'Sawmill')), ( ((19, 23), 'Sawmill')), ( ((23, 28), 'Sawmill')), ( ((30, 21), 'Sawmill')), ( ((28, 21), 'Sawmill')), ( ((25, 26), 'Sawmill')), ( ((28, 24), 'Sawmill')), ( ((29, 29), 'Sawmill')), ( ((25, 30), 'Sawmill')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
episode = [( ((31, 24), 'Sawmill')), None, None, None, ( ((26, 27), 'Sawmill')), ( ((22, 28), 'Sawmill')), ( ((30, 28), 'Sawmill')), ( ((23, 27), 'Sawmill')), ( ((32, 19), 'Sawmill')), ( ((32, 30), 'Sawmill')), ( ((21, 19), 'Sawmill')), ( ((26, 28), 'Barack')), ( ((27, 19), 'Barack')), ( ((21, 29), 'Barack')), ( ((32, 22), 'Barack')), ( ((23, 29), 'Barack')), ( ((24, 26), 'Barack')), ( ((29, 30), 'Barack')), ( ((18, 18), 'Barack')), ( ((26, 21), 'Barack')), ( ((20, 20), 'Barack')), ( ((29, 28), 'Barack')), ( ((25, 23), 'Barack')), ( ((19, 23), 'Barack')), ( ((24, 32), 'Barack')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]


environment_data = load_environment_data()
# TODO: merge control and env?
environment, control = instanciate_environment(*environment_data)

game_move_nr = 0
for _ in control.yieldloop():
    game_move_nr += 1

    if game_move_nr % 2 == 1:

        if game_move_nr < 2 * len(episode):

            action = None
            if episode[game_move_nr//2]:
                action = (GameEvent.CONSTRUCT_BUILDING, episode[game_move_nr//2])

            print(action)
            if action:
                environment.add_game_event(*action)

        if game_move_nr >= 2 * NUM_EPISODE_HORIZON_OBSERVED:
            break
        elif game_move_nr > 1:
            agent.append_trajectory((get_extended_score(environment),
                                     *last_state_action,
                                     extract_state(environment)))
        last_state_action = [extract_state(environment), action]

agent.end_episode(True)