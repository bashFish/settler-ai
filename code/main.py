from multiprocessing.managers import BaseManager
from map import initialize_map

from ui import SettlerUi
from state import State
import json
import random
import time
import numpy as np

from multiprocessing import Process, Manager


random.seed(10)


#TODO: static!
class Config:
    def __init__(self):
        self.read_configs()

    def read_configs(self):
        with open('config/buildings.json') as fp:
            self.buildings = json.load(fp)
        with open('config/colors.json') as fp:
            self.colors = json.load(fp)


# fetches events of both ui and state,
#   processes and forwards them to the other component
class Game:
    def __init__(self, state):
        self.state = state

        #TODO: initialize ui with state/ draw shit
        #self.update_ui_gamestats_text()
        #self.update_ui_ticks_text()

    #def update_ui_gamestats_text(self):
    #    self.ui.update_gamestats_text()

    #def update_ui_ticks_text(self):
    #    self.ui.update_ticks_text()

    def mainloop(self):
        ls_occ, ls_ra = initialize_map(self.state.get_landscape_occupation(), self.state.get_landscape_resource_amount())
        self.state.set_landscape_occupation_complete(ls_occ)
        self.state.set_landscape_resource_amount_complete(ls_ra)

        while True:
            print("Game Iteration")
            time.sleep(1)


def game_loop(shared_state):
    g = Game(shared_state)
    g.mainloop()


def ui_loop(shared_state):
    ui = SettlerUi(shared_state)
    ui.mainloop()


if __name__ == "__main__":
    """
    So, this
    approach is not well
    recommended
    for multiprocessing case.It's always better if you can use low-level tools like lock/semaphore/pipe/queue or high-level tools like Redis queue or Redis publish/subscribe for complicated use case (only my recommendation lol).
    """

    BaseManager.register('State', State)
    manager = BaseManager()
    manager.start()
    s = manager.State()

    c = Config()

    gp = Process(target=game_loop, args=(s, ))
    gp.start()
    up = Process(target=ui_loop, args=(s, ))
    up.start()

    gp.join()
    up.join()