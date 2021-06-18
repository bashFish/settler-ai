import random
from events import GameEvent
import numpy as np


#TODO: in theory/ later you can also get ressources dropping buildings
def is_state_dead_end(state, buildings):
    for building_key in buildings:
        if 'construction' in buildings[building_key]:
            buildable = True
            for ressource in buildings[building_key]['construction']['cost']:
                if buildings[building_key]['construction']['cost'][ressource] > state[1][ressource]:
                    buildable = False
            if buildable:
                return False
    return True


def generate_random_valid_action(key_to_building, state):
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
    #    environment.add_game_event(GameEvent.END_GAME)
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


#TODO: this is going to be replaced by a target player!
# let ais play against each other
# this player does not generalize to other maps!
def get_best_player_move_randomized(key_to_building, top_10_games, state, move):
    #highest = max((sc[0], it) for it, sc in enumerate(top_10_games))
    highest = top_10_games[-1]
    key, cell_r = generate_random_valid_action(key_to_building, state)
    if random.random() > .9 or highest[0] < 0:   # 10 % total random moves
        return key, cell_r
    else:
        current = -1
        while current > -8 and top_10_games[current-1][0] > 0 and random.random() > .8:
            current -= 1
        key,_, cell = top_10_games[current][1][move]
        if random.random() > .95:
            while not cell_r:
                _, cell_r = generate_random_valid_action(key_to_building, state)
            cell = cell_r

    return key, cell


# @deprecated
def enqueue_random_action(all_keys, key_to_building, state):
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