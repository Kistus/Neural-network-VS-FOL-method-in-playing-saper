import numpy as np
import tensorflow as tf
from neuralnet.transformer import get_network_input_for_board
from board import Board
from minesweeper import Minesweeper

model = tf.keras.models.load_model('mymodel.h5')


def solve(game):
    random_x = np.random.randint(game.cols) # Get random position (x)
    random_y = np.random.randint(game.rows) # Get random position (y)
    game.click(random_x, random_y) # Click on random position
    while not game.ended:
        x_vals, y_vals, network_input = get_network_input_for_board(game.visible_board)
        predictions = model.predict(network_input).flatten()
        best_idx = predictions.argmax()

        x = int(x_vals[best_idx])
        y = int(y_vals[best_idx])
        game.click(x, y)
    return game.won


def test_multiple_games(n, size, mines):
    games_won = 0
    games_lost = 0
    completeness = []
    for _ in range(n):
        board = Board.generate(size, mines)
        game = Minesweeper(board)
        if solve(game):
            games_won += 1
            print("Game won", end='')
        else:
            games_lost += 1
            print("Game lost", end='')
        game_completeness = (game.visible_board.contents.symbols == ord('#')).sum()/(game.cols * game.rows)
        completeness.append(game_completeness)
        print(' Completeness: ', game_completeness)
    completeness = np.array(completeness)
    avg_completeness = completeness.mean()
    median_completeness = np.median(completeness)
    print(
        f'During {n} tests on board of size {size} with {mines} mines neural network agent won {games_won}'
        f' and lost {games_lost} times, with average completeness {avg_completeness}, and median {median_completeness}')


test_multiple_games(100, 9, 9)