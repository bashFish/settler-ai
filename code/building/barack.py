from factory import Factory
from building import Building


class BarackFactory(Factory):
    def __init__(self, config):
        self._config = config

    def instanciate(self):
        return Barack(self._config)


class Barack(Building):
    def __init__(self, config):
        pass
