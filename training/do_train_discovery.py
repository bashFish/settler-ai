
from training.agents.DiscoverAgent import DiscoverAgent
from training.trainAgent import train_loop

epsilon_greedy = .15
num_episodes = 1000*50


if __name__ == '__main__':

    discover_agent = DiscoverAgent(discount_factor=0.9, reward_lookahead=1, epsilon_greedy=epsilon_greedy)
    agent = discover_agent

    train_loop(agent, num_episodes)