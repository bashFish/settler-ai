import json


class State:
    def __init__(self):
        with open('config/initial_state.json') as fp:
            self.state_dict = json.load(fp)

    @property
    def settler(self):
        return self.state_dict['settler']

    @property
    def wood(self):
        return self.state_dict['wood']

    @property
    def plank(self):
        return self.state_dict['plank']

    def __repr__(self):
        return "settler: %i  wood: %i  plank: %i" % (self.settler, self.wood, self.plank)