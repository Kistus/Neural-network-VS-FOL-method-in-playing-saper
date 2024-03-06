import numpy as np
import tensorflow as tf
from neuralnet.datagenerator import transform_input_board
from symbols import CLOSED_SYMBOL

threshold = 0.1

model = tf.keras.models.load_model('model4.h5')

#model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])


def agent(game):
    while not game.ended:
        symbols = game.visible_board.contents.symbols
        values = game.visible_board.contents.values
        network_input = np.ndarray((1, 162))
        network_input[0] = transform_input_board(symbols, values)
        can_be_clicked = (symbols == ord(CLOSED_SYMBOL)).transpose().reshape((81,))
        predicted_values = model.predict(network_input)[0]
        predicted_values *= can_be_clicked
        if predicted_values.max() <= threshold:
            position_no = np.random.randint(1, can_be_clicked.sum()+1)
            for i in range(81):
                if can_be_clicked[i]:
                    position_no -= 1
                    if position_no == 0:
                        x = i % 9
                        y = i // 9
                        game.click(int(x), int(y))
        else:
            position = predicted_values.argmax()
            y = position // 9
            x = position % 9
            game.click(int(x), int(y))
    return game.won
