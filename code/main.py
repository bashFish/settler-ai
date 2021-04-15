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


# fetches events of both ui and state,
#   processes and forwards them to the other component
class Game:
    def __init__(self, state, ui):
        self.state = state
        self.ui = ui
        #TODO: initialize ui with state/ draw shit


if __name__ == "__main__":
    c = Config()
    s = State()
    ui = SettlerUi()
    g = Game(s, ui)
    #TODO: make ui slim and passive as possible! other components send events there
    ui.mainloop()