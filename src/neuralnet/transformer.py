from symbols import CLOSED_SYMBOL
import numpy as np

NUM_OF_CLASSES = 12
NUM_OF_NEIGHBOURS = 48


def get_network_input_for_board(board):
    board_symbols = board.contents.symbols
    closed_symbols = (board_symbols == ord(CLOSED_SYMBOL)).transpose()
    closed_symbols_num = closed_symbols.sum()
    X_values = np.zeros((closed_symbols_num, ), np.uint32)
    Y_values = np.zeros((closed_symbols_num,), np.uint32)
    network_input = np.zeros((closed_symbols_num, NUM_OF_CLASSES*NUM_OF_NEIGHBOURS), np.float32)
    flat_closed_symbols = closed_symbols.flatten()
    j = 0
    divisor = board.size
    for i in range(board.size ** 2):
        if flat_closed_symbols[i]:
            y = i // divisor
            x = i % divisor
            X_values[j] = x
            Y_values[j] = y
            network_input[j] = get_network_input_for_position(board_symbols, x, y)
            j += 1
    return X_values, Y_values, network_input


def get_network_input_for_position(board_contents, x, y):
    board_fragment = get_board_fragment(board_contents, x, y)
    return classify_elements(board_fragment)


def get_neighbours(x, y, distance):
    element = 0
    elements = (2 * distance + 1) ** 2 - 1
    x_vals = np.ndarray((elements,), np.uint32)
    y_vals = np.ndarray((elements,), np.uint32)
    for i in range(-distance, distance+1):
        for j in range(-distance, distance+1):
            if i == 0 and j == 0:
                continue
            x_vals[element] = x + i
            y_vals[element] = y + i
            element += 1
    return x_vals, y_vals


# Finds nearest neighbours and gets their values (if the neighbour doesn't exist 255 is it's value)
def get_board_fragment(board_contents, x, y):
    X_values, Y_values = get_neighbours(x, y, 3)
    accessible_x_vals = np.logical_and((X_values >= 0), (X_values < board_contents.shape[0]))
    accessible_y_vals = np.logical_and((Y_values >= 0), (Y_values < board_contents.shape[1]))
    accessible_values = np.logical_and(accessible_x_vals, accessible_y_vals)
    result = np.zeros(accessible_values.shape, np.uint8)
    for i in range(8):
        if accessible_values[i]:
            result[i] = board_contents[X_values[i], Y_values[i]]
        else:
            result[i] = 255
    return result


# Performs one-hot encoding on the board fragment
def classify_elements(content_values):
    flat_content_values = content_values.flatten()
    size = flat_content_values.shape[0]
    classes = [ord(CLOSED_SYMBOL), ord(' '), ord('1'), ord('2'), ord('3'), ord('4'),
               ord('5'), ord('6'), ord('7'), ord('8'), ord('9'), 255]
    result = np.zeros((len(classes), size), np.float32)
    for i, class_element in enumerate(classes):
        result[i] = (flat_content_values == class_element) * 1.0
    return result.flatten()
