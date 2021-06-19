import pickle
from collections import deque
import random
import time
import numpy as np
import tensorflow as tf

from events import GameEvent
from misc import path_append
from training.misc.ModifiedTensorBoard import ModifiedTensorBoard
from training.agents.Agent import Agent
from training.misc.model_misc import model_action, extract_state

from training.misc.training_misc import NUM_EPISODE_HORIZON_CONTROLLED, TRAIN_MIN_REPLAY_MEMORY_SIZE, \
    TRAIN_MINIBATCH_SIZE, \
    TRAIN_UPDATE_TARGET_STEPS, TRAIN_MODEL_NAME, TRAIN_MEMORY_SIZE, get_pseudo_random_position, get_current_timestring, \
    get_memory_from_current_episode


class DQNAgent(Agent):
    def __init__(self, discount_factor, reward_lookahead, epsilon_greedy = .01):
        super().__init__()

        self.choosable_keys = ['s', 'w', 'k', '-']
        self.epsilon_greedy = epsilon_greedy

        self.replay_memory = deque(maxlen=TRAIN_MEMORY_SIZE)
        self.discount_factor = discount_factor
        self.reward_lookahead = reward_lookahead

        self.current_action_model = model_action(0.001)
        self.target_action_model = model_action(0.001)
        self.current_update_counter = 0

        log_dir_name = "logs/{}-{}".format(TRAIN_MODEL_NAME, int(time.time()))
        self.tensorboard = ModifiedTensorBoard(TRAIN_MODEL_NAME, log_dir=log_dir_name)
        self.train_summary_writer = tf.summary.create_file_writer(log_dir_name)
        self.current_episode = 0


    def end_episode(self, print_trajectory):
        self.replay_memory.extend(get_memory_from_current_episode(self.current_episode_trajectories, self.buildings, self.discount_factor, self.reward_lookahead))
        if print_trajectory:
            print("score: %s"%(self.current_episode_trajectories[-1][0]))
            print([x[2] for x in self.current_episode_trajectories])
        self.current_episode_trajectories = []
        self.current_episode += 1

    def choose_action(self, environment):

        if random.random() < self.epsilon_greedy:
            key = random.choice(self.choosable_keys)
            if key == '-':
                return None
        else:
            state = extract_state(environment)
            predictions = self.current_action_model.predict(self.state_to_model_input(state))
            action_index = np.argmax(predictions)

            if action_index == 4:
                return None

            key = self.building_keys[action_index]

        building = self.key_to_building[key]

        return (GameEvent.CONSTRUCT_BUILDING,
                (self.choose_cell_on_creation_action(environment, key), building))

    def _action_to_index(self, action):
        if action is None:
            return 4
        return self.building_keys.index(self.buildings[action[1][1]]['key'])

    def choose_cell_on_creation_action(self, environment, building_key):
        #current_coord_model = self.current_coords_models[self.building_keys.index(building_key)]
        #return prediction_to_coords(current_coord_model.predict(state[0]))
        return get_pseudo_random_position(environment, building_key)

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

        with self.train_summary_writer.as_default():
            tf.summary.histogram('predictions', current_qs_list, step=self.current_episode)

        next_current_states = self.state_list_to_model_input(minibatch, 2)
        future_qs_list = self.target_action_model.predict(next_current_states)

        #TODO: clip rewards
        y = []
        for index, (current_state, action, new_current_state, reward, flexible_reward) in enumerate(minibatch):

            if flexible_reward:
                max_future_q = np.max(future_qs_list[index])
                reward += self.discount_factor * max_future_q

            current_qs = current_qs_list[index]
            current_qs[self._action_to_index(action)] = reward

            y.append(current_qs)

        self.current_action_model.fit(current_states, np.array(y), batch_size=TRAIN_MINIBATCH_SIZE,
                       verbose=0, shuffle=False, callbacks=[self.tensorboard])

        self.current_update_counter += 1
        if self.current_update_counter > TRAIN_UPDATE_TARGET_STEPS:
            self.target_action_model.set_weights(self.current_action_model.get_weights())
            self.current_update_counter = 0

    def save(self):
        current_timestamp = get_current_timestring()
        self.target_action_model.save(path_append('training/models/dqn/%s'%(current_timestamp)))
        pickle.dump(self.replay_memory, open(path_append('training/models/dqn/%s_replay_memory.pckl'%(get_current_timestring())), 'wb'))
        print("saved %s"%(current_timestamp))

    def load(self, time_string):
        self.target_action_model = tf.keras.models.load_model(path_append('training/models/dqn/%s'%(time_string)))