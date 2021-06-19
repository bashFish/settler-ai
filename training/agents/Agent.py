import pickle
from abc import ABC, abstractmethod

from misc import parse_buildings, path_append


class Agent(ABC):
    def __init__(self):
        self.buildings, self.key_to_building, self.objectid_to_buildings = parse_buildings()
        self.building_keys = list(self.key_to_building.keys())

        self.current_episode_trajectories = []
        self.replay_memory = None

    def __repr__(self):
        return "I can speak, too"

    def append_trajectory(self, trajectory):
        self.current_episode_trajectories.append(trajectory)

    @abstractmethod
    def load(self, name):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def choose_action(self, environment):
        pass

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def end_episode(self, print_trajectory):
        pass

    def load_replay_memory(self, path):
        self.replay_memory.extend(pickle.load(open(path_append(path), 'rb')))