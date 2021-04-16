from multiprocessing.managers import BaseManager
from multiprocessing import Process

from ui import Ui
from game import Game
from state import State
import random


random.seed(10)


def game_loop(shared_state):
    g = Game(shared_state)
    g.mainloop()


def ui_loop(shared_state):
    ui = Ui(shared_state)
    ui.mainloop()


if __name__ == "__main__":

    BaseManager.register('State', State)
    manager = BaseManager()
    manager.start()
    s = manager.State()

    gp = Process(target=game_loop, args=(s, ))
    gp.start()
    up = Process(target=ui_loop, args=(s, ))
    up.start()

    gp.join()
    up.join()
