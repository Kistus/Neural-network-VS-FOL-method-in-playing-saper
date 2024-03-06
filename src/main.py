import time

import pandas as pd
from agent import Agent as FOLAgent
from neuralagent import Agent as NeuralAgent
from board import Board
from minesweeper import Minesweeper

AGENTS = [FOLAgent, NeuralAgent]

def single_performance_measure(agent, game):
    t = time.process_time()
    agent.solve(game)
    elapsed_time = time.process_time() - t
    return {
        'won': game.won,
        'lost': game.lost,
        'size': game.size,
        'elapsed_time': elapsed_time,
        'last_move_random': agent.last_move_random,
        'agent': agent.name()
    }


def create_agents(board_size):
    return list(map(lambda agent: agent(board_size), AGENTS))


def get_random_game(board_size, mines):
    return Minesweeper(Board.generate(board_size, mines))


def measure_agents(board_size, mines, measurements):
    agents = create_agents(board_size)
    dataset = []
    for agent in agents:
        for _ in range(measurements):
            game = get_random_game(board_size, mines)
            measurement = single_performance_measure(agent, game)
            dataset.append(measurement)
    return pd.DataFrame(dataset)

def mines_amount(size):
    return int(size * size * 0.07)

def main():
    mines = 7
    size = 8
    sizes = [8, 10, 12, 14, 16, 18]
    tests = 100
    measurements = []

    for size in sizes:
        mines = mines_amount(size)
        measurement = measure_agents(size, mines, tests)
        measurements.append(measurement)
        print(f'Testing agents, size = {size}, mines = {mines}, tests = {tests} per agent')

    combined_measurement = pd.concat(measurements, ignore_index=True)
    combined_measurement.to_csv('results.csv', index=False)
#measurement = measure_agents(size, mines, tests)
    #print(f'Testing agents, size = {size} , mines = {mines}, tests =  {tests} per agent')
    #measurement.to_csv(r"/Users/mariiakyrychenko/Downloads/Telegram Desktop/neusuka/SI_project/SI_project/src/results.csv", index=False)

if __name__ == '__main__':
    main()
