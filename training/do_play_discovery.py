from events import GameEvent
from training.agents.DiscoverAgent import DiscoverAgent
from training.misc.model_misc import *
from training.misc.training_misc import *
from training.trainAgent import get_extended_score

discover_agent = DiscoverAgent(discount_factor=0.9, reward_lookahead=1, epsilon_greedy=.1)
agent = discover_agent

#episode = [( ((28, 25), 'Barack')), None, ( ((19, 21), 'Woodcutter')), None, ( ((23, 23), 'Sawmill')), ( ((18, 18), 'Sawmill')), ( ((26, 23), 'Sawmill')), ( ((24, 23), 'Sawmill')), ( ((20, 20), 'Sawmill')), ( ((26, 28), 'Sawmill')), ( ((29, 27), 'Sawmill')), ( ((19, 23), 'Sawmill')), ( ((23, 28), 'Sawmill')), ( ((30, 21), 'Sawmill')), ( ((28, 21), 'Sawmill')), ( ((25, 26), 'Sawmill')), ( ((28, 24), 'Sawmill')), ( ((29, 29), 'Sawmill')), ( ((25, 30), 'Sawmill')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
episode = [( ((21, 19), 'Sawmill')), ( ((28, 19), 'Woodcutter')), None, None, ( ((27, 26), 'Barack')), None, None, None, None, None, ( ((26, 32), 'Barack')), None, None, None, ( ((32, 21), 'Barack')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
episode = [( ((27, 19), 'Woodcutter')), ( ((25, 20), 'Woodcutter')), ( ((28, 21), 'Woodcutter')), None, None, None, None, None, None, None, ( ((30, 21), 'Woodcutter')), None, None, None, ( ((27, 22), 'Woodcutter')), None, None, None, ( ((23, 20), 'Woodcutter')), None, None, None, ( ((29, 19), 'Woodcutter')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
episode = [( ((20, 20), 'Sawmill')), None, None, ( ((32, 23), 'Sawmill')), None, None, None, ( ((25, 18), 'Sawmill')), None, None, None, None, None, None, None, None, None, ( ((30, 30), 'Barack')), ( ((23, 24), 'Sawmill')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
episode = [( ((29, 22), 'Woodcutter')), ( ((18, 18), 'Woodcutter')), ( ((25, 22), 'Woodcutter')), ( ((31, 19), 'Woodcutter')), ( ((21, 20), 'Woodcutter')), ( ((32, 21), 'Woodcutter')), ( ((28, 19), 'Woodcutter')), ( ((22, 20), 'Woodcutter')), ( ((20, 20), 'Woodcutter')), ( ((20, 19), 'Woodcutter')), ( ((20, 18), 'Woodcutter')), ( ((29, 18), 'Woodcutter')), ( ((25, 18), 'Woodcutter')), ( ((30, 21), 'Woodcutter')), ( ((26, 20), 'Woodcutter')), ( ((22, 22), 'Woodcutter')), ( ((23, 19), 'Woodcutter')), ( ((26, 18), 'Woodcutter')), ( ((32, 18), 'Woodcutter')), ( ((22, 21), 'Woodcutter')), ( ((29, 19), 'Woodcutter')), ( ((30, 22), 'Woodcutter')), ( ((21, 18), 'Woodcutter')), ( ((31, 21), 'Woodcutter')), ( ((20, 22), 'Woodcutter')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]


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