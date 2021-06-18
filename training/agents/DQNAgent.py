from collections import deque
import random
import time
import numpy as np

from events import GameEvent
from training.misc.ModifiedTensorBoard import ModifiedTensorBoard
from training.agents.Agent import Agent
from training.misc.game_misc import is_state_dead_end
from training.misc.model_misc import model_action, model_coordinates, prediction_to_coords, extract_state

from training.misc.training_misc import NUM_EPISODE_HORIZON_CONTROLLED, TRAIN_MIN_REPLAY_MEMORY_SIZE, TRAIN_MINIBATCH_SIZE, \
    TRAIN_UPDATE_TARGET_STEPS, TRAIN_MODEL_NAME, TRAIN_MEMORY_SIZE


class DQNAgent(Agent):
    def __init__(self, discount_factor, reward_lookahead):
        super().__init__()

        self.replay_memory = deque(maxlen=TRAIN_MEMORY_SIZE)
        self.discount_factor = discount_factor
        self.reward_lookahead = reward_lookahead

        self.current_action_model = model_action(0.001)
        self.target_action_model = model_action(0.001)
        self.current_coords_models = [model_coordinates() for i in range(self.building_keys)]
        self.target_coords_models = [model_coordinates() for i in range(self.building_keys)]
        self.current_update_counter = 0

        self.tensorboard = ModifiedTensorBoard(TRAIN_MODEL_NAME, log_dir="logs/{}-{}".format(TRAIN_MODEL_NAME, int(time.time())))


    #TODO: later don't take entire episode but only recent X moves + Y sampled moves from before
    def get_memory_from_current_episode(self):
        #computes reward from score (or dead end)
        # returns [[ state action nextstate reward ]_i for i]

        # 1st case: dead end -> rate entire X steps from trajectory with discount 'as bad'
        if is_state_dead_end(self.current_episode_trajectories[-1][1], self.buildings):
            last_good_index = len(self.current_episode_trajectories) - 2
            while last_good_index > 0:
                if not is_state_dead_end(self.current_episode_trajectories[last_good_index][1], self.buildings):
                    break
                last_good_index -= 1

            episode_rewards = [0] * len(last_good_index)
            current_index = last_good_index - 1
            episode_rewards[current_index] = -1
            for _ in range(last_good_index-1):
                current_index -= 1
                episode_rewards[current_index] = episode_rewards[current_index+1]*self.discount_factor

            return [list(self.current_episode_trajectories[i][1:])+[episode_rewards[i], 0] for i in range(last_good_index)]

        # 2nd case: bellmann equation:
        resultset = []
        for i in range(NUM_EPISODE_HORIZON_CONTROLLED):
            resultset.append(list(self.current_episode_trajectories[i][1:]) +
                [sum([(self.current_episode_trajectories[1+j+i][0]-self.current_episode_trajectories[j+i][0])*self.discount_factor**j for j in range(self.reward_lookahead)]), 1])
        return resultset


    def end_episode(self):
        self.replay_memory.extend(self.get_memory_from_current_episode())
        self.current_episode_trajectories = []

    def choose_action(self, environment):
        state = extract_state(environment)
        action_index = np.argmax(self.current_action_model.predict(self.state_to_model_input(state)))

        if action_index == 4:
            return None

        building = self.key_to_building[self.building_keys[action_index]]

        return (GameEvent.CONSTRUCT_BUILDING,
                (self.choose_cell_on_creation_action(state, building), building))

    def _action_to_index(self, key):
        if key is None:
            return 4
        return self.building_keys.index(self.buildings[key[1][1]]['key'])

    def choose_cell_on_creation_action(self, state, building):
        current_coord_model = self.current_coords_models[self.building_keys.index(self.buildings[building]['key'])]
        return prediction_to_coords(current_coord_model.predict(state[0]))

    def choose_random_available_cell(self, state):
        possible = np.where(state[0][2] == 1) # maps array / owned terrain = 1
        position = random.randint(0, len(possible[0])-1)
        return possible[0][position], possible[1][position]

    def state_list_to_model_input(self, state_list, index):
        tmp = [self.state_to_model_input(trajectory[index]) for trajectory in state_list]
        return {'map_state': np.vstack([t['map_state'] for t in tmp]),
                'statistic_state': np.vstack([t['statistic_state'] for t in tmp])}

    def state_to_model_input(self, state):
        return {'map_state': np.stack([state[0]]),
                'statistic_state': np.array([list(state[1].values()) + list(state[2:])])}

    def train(self):
        if len(self.replay_memory) < TRAIN_MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.replay_memory, TRAIN_MINIBATCH_SIZE)

        current_states = self.state_list_to_model_input(minibatch, 0)
        current_qs_list = self.current_action_model.predict(current_states)

        next_current_states =  self.state_list_to_model_input(minibatch, 2)
        future_qs_list = self.target_action_model.predict(next_current_states)

        #TODO: clip rewards
        y = []
        for index, (current_state, action, new_current_state, reward, flexible_reward) in enumerate(minibatch):

            if flexible_reward:
                max_future_q = np.max(future_qs_list[index])
                reward += self.discount_factor * max_future_q

            current_qs = current_qs_list[index]
            current_qs[self._action_to_index(action)] = reward

            if action:
                #TODO: how to update coord model? only got score :/
                # positive -> keep, othw -> random ? or a best/selector chooser?
                #TODO: just as with target, don't train coords and building at same time?
                #current_coord_model = self.current_coords_models[
                #    self.building_keys.index(self._action_to_index(action))]
                #current_coord_model.fit()
                #TODO: pick from random agent best move.
                pass

            y.append(current_qs)

        self.current_action_model.fit(current_states, np.array(y), batch_size=TRAIN_MINIBATCH_SIZE,
                       verbose=0, shuffle=False, callbacks=[self.tensorboard])

        self.current_update_counter += 1
        if self.current_update_counter > TRAIN_UPDATE_TARGET_STEPS:
            self.target_action_model.set_weights(self.current_action_model.get_weights())
            self.current_update_counter = 0
