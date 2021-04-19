import time

from control import Control
from events import GameEvent
from misc import parse_buildings
from state import State
import random


buildings, key_to_building, objectid_to_building = parse_buildings()
rows, cols = 50, 50

all_keys = list(key_to_building.keys())
all_keys.extend(['d', 'q'])



def enqueue_random_action(state):
    #TODO: start directly with search tree! only valid moves for starters.
    key = random.choice(all_keys)
    x, y = random.randint(0,50), random.randint(0,50)
    cell = (x,y)

    print("added action: %s %s" %(key, cell))
    if key == 'd':
        state.add_game_event(GameEvent.DROP, cell)
    elif key == 'q':
        state.add_game_event(GameEvent.END_GAME)
    else:
        state.add_game_event(GameEvent.CONSTRUCT_BUILDING, (cell, key_to_building[key]))



#TODO: copied configs!
if __name__ == '__main__':

    print("h")
    s = State()
    g = Control(s)

    for r in g.yieldloop():
        enqueue_random_action(s)

    print("Final score: %s/ %s"%(s.get_score(),s.get_ticks()))