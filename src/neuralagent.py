import numpy as np
import tensorflow as tf
from transformer import get_network_input_for_board


model = tf.keras.models.load_model(r'/Users/mariiakyrychenko/Downloads/Telegram Desktop/neusuka/SI_project/SI_project/src/mymodel.h5')
NUM_OF_CLASSES = 12
NUM_OF_NEIGHBOURS = 48

class Agent:

    def __init__(self, *_):
        self.last_move_random = True
        pass

    def solve(self, game):
        random_x = np.random.randint(game.cols)  # Get random position (x)
        random_y = np.random.randint(game.rows)  # Get random position (y)
        game.click(random_x, random_y)  # Click on random position
        while not game.ended:
            x_vals, y_vals, network_input = get_network_input_for_board(game.visible_board)
            predictions = model.predict(network_input).flatten()
            best_idx = predictions.argmax()
            x = int(x_vals[best_idx])
            y = int(y_vals[best_idx])
            game.click(x, y)
            self.last_move_random = False
        return game.won

    def name(self):
        return 'neural'
