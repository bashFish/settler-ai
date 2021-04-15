from ui import SettlerUi
from state import State
import json


#TODO: static!
class Config:
    def __init__(self):
        self.read_configs()

    def read_configs(self):
        with open('config/buildings.json') as fp:
            self.buildings = json.load(fp)
        with open('config/colors.json') as fp:
            self.colors = json.load(fp)


class Game:
    def __init__(self, state):
        self.state = state


if __name__ == "__main__":
    c = Config()
    s = State()
    g = Game(s)
    SettlerUi(s).mainloop()