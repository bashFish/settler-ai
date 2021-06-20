from events import GameEvent
import numpy as np
from training.misc.training_misc import instanciate_environment, load_environment_data
from training.trainAgent import get_extended_score

episode = [( ((19, 21), 'Sawmill')), None, None, None, None, ( ((31, 21), 'Woodcutter')), ( ((24, 18), 'Woodcutter')), ( ((32, 20), 'Barack')), ( ((26, 21), 'Barack')), ( ((18, 27), 'Barack')), ( ((28, 20), 'Woodcutter')), ( ((23, 18), 'Woodcutter')), ( ((23, 20), 'Woodcutter')), ( ((22, 22), 'Woodcutter')), ( ((19, 19), 'Woodcutter')), ( ((27, 21), 'Woodcutter')), ( ((31, 18), 'Woodcutter')), ( ((25, 20), 'Woodcutter')), ( ((21, 20), 'Woodcutter')), ( ((26, 22), 'Barack')), ( ((24, 26), 'Barack')), ( ((24, 25), 'Barack')), ( ((25, 21), 'Barack')), ( ((23, 21), 'Barack')), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

if __name__ == '__main__':

    environment_data = load_environment_data()
    environment, control = instanciate_environment(*environment_data)

    cur_action_pos = 0
    for _ in control.yieldloop():
        action = episode[cur_action_pos]
        print("action %s %s"%(cur_action_pos, action))

        if action:
            environment.add_game_event(GameEvent.CONSTRUCT_BUILDING, action)

        print([b for b in environment.buildings if b.finished is True])
        print([b for b in environment.buildings if b.finished is False])
        print(environment.state_dict)
        print(environment.produced_dict)
        print(np.sum(environment.owned_terrain))
        print("%s %s"%(environment.get_score(), get_extended_score(environment)))

        cur_action_pos += 1
        if cur_action_pos >= len(episode):
            break
        print("")