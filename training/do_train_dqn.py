from training.agents.DQNAgent import DQNAgent
from training.trainAgent import train_loop

LOAD_MODEL = '20210622_12_20_9998'

epsilon_greedy = .2
num_episodes = 1000*10 -1


if __name__ == '__main__':

    dqn_agent = DQNAgent(discount_factor=0.95, reward_lookahead=1, epsilon_greedy=epsilon_greedy)
    #dqn_agent.load_replay_memory('training/models/dqn/20210622_12_20_9998_replay_memory.pckl')

    agent = dqn_agent

    if LOAD_MODEL:
        agent.load(LOAD_MODEL)

    train_loop(agent, num_episodes, 1000)