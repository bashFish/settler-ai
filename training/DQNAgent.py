import random
import numpy as np
from events import GameEvent
from misc import parse_buildings
from training.model_misc import model_action, model_coordinates
from abc import ABC, abstractmethod


class Agent(ABC):

    def __init__(self):
        self.buildings, self.key_to_building, self.objectid_to_buildings = parse_buildings()

        self.building_keys = list(self.key_to_building.keys())

    @abstractmethod
    def get_action(self, state):
        pass


class RandomAgent(Agent):

    def __init__(self, construct_probability):
        super().__init__()
        self.construct_probability = construct_probability

    def get_action(self, state):

        action_category = random.random()
        action = None

        """ TODO: no delete yet
        if action_category < .05 and False: 
            b = random.choice(state.buildings)
            action = (GameEvent.DROP, (b.coordinate))
        """

        if action_category > self.construct_probability:
            key = random.choice(self.building_keys)

            available_positions = np.stack(np.where(state.get_owned_terrain() == 1)).transpose()
            while True:
                coordinates = random.choice(available_positions)
                if state.check_coordinates_buildable(coordinates):
                    break

            action = (GameEvent.CONSTRUCT_BUILDING, (coordinates, self.key_to_building[key]))

        return action



class DQNAgent(Agent):
    def __init__(self):
        m_action = model_action()
        m_coords = model_coordinates()

    def update_environment(self):
        pass

    def predict(self):
        prediction = m_action.predict(state_representation_vector(s, old_gambled_states))
        prediction_2 = m_coords.predict(state_representation_vector_2(s, old_gambled_states, building))

        coords = prediction_to_coords(prediction_2[0])
        GameEvent.CONSTRUCT_BUILDING, (coords, key_to_building[predict_key])
