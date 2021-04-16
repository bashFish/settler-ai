import time
from map import initialize_map
import json


with open('config/game.json') as fp:
    gameconf = json.load(fp)

with open('config/buildings.json') as fp:
    buildings = json.load(fp)


# fetches events of both ui and state,
#   processes and forwards them to the other component
class Game:
    def __init__(self, state):
        self.state = state

    def update(self):
        self.state.increment_tick()

    def mainloop(self):

        #TODO: geht das wirklich nicht besser? kommt mir sehr ineffizient vor,
        # wenn die prozesse so mühseelig nen state updaten müssen :/
        ls_occ, ls_ra = initialize_map(self.state.get_landscape_occupation(), self.state.get_landscape_resource_amount())
        self.state.set_landscape_occupation_complete(ls_occ)
        self.state.set_landscape_resource_amount_complete(ls_ra)

        while True:
            start = time.time()
            self.update()
            sleep = gameconf['tick_rate'] - (time.time() - start)

            if sleep > 0.:
                time.sleep(sleep)