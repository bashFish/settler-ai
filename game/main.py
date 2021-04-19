from multiprocessing.managers import BaseManager
from multiprocessing import Process

from ui import Ui
from control import Control
from state import State
import random


random.seed(10)


def game_loop(shared_state):
    g = Control(shared_state)
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

    up.join()
    # gp.join() if ui crashes, program is exited