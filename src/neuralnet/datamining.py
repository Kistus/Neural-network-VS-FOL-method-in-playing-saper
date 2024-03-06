from board import Board
from minesweeper import Minesweeper
from symbols import MINE_SYMBOL
from neuralnet.transformer import get_network_input_for_board
import numpy as np

# Mining process:
# 1. Generate a random board
# 2. Make random number of random (non-losing moves)
# 3. Take the visible board and real board and get information wheather you can mine the data

def mine_through_game(game: Minesweeper):
    X_values, Y_values, network_inputs = get_network_input_for_board(game.visible_board)
    network_results = np.zeros((len(X_values),), np.float32)
    for i in range(len(X_values)):
        element_value = game.real_board.contents.symbols[X_values[i], Y_values[i]]
        if element_value != ord(MINE_SYMBOL):
            network_results[i] = 1.0
    return network_inputs, network_results

def get_random_possible_game(size, mines, max_clicks):
    game = Minesweeper(Board.generate(size, mines))
    num_clicks = np.random.randint(1, max_clicks+1)
    i = 0
    while i < num_clicks:
        position = np.random.randint(0, size**2)
        x = position % size
        y = position // size
        if game.real_board.contents[x, y] != ord(MINE_SYMBOL):
            game.click(x, y)
            i += 1
    return game

def get_possible_inputs_for_game(size, mines, max_clicks):
    return mine_through_game(get_random_possible_game(size, mines, max_clicks))