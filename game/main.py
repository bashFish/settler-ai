from multiprocessing.managers import BaseManager
from multiprocessing import Process
import multiprocessing

from ui import Ui
from control import Control
from environment import Environment
import random


random.seed(10)


def game_loop(shared_environment):
    g = Control(shared_environment)
    g.mainloop()


def ui_loop(shared_environment):
    ui = Ui(shared_environment)
    ui.mainloop()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    BaseManager.register('Environment', Environment)
    manager = BaseManager()
    manager.start()
    environment = manager.Environment()

    gp = Process(target=game_loop, args=(environment,))
    gp.start()
    up = Process(target=ui_loop, args=(environment,))
    up.start()

    up.join()
    # gp.join() if ui crashes, program is exited