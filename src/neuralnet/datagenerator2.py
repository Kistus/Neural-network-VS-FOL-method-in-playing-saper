import numpy as np
from board import Board
from itertools import repeat
from minesweeper import Minesweeper
from symbols import EMPTY_SYMBOL
from copy import deepcopy


def get_micro_board(board: Board, center_x, center_y):
    micro_board_symbols = np.ndarray((9, 9), np.uint8)
    min_x, max_x = center_x - 5, center_x + 5
    min_y, max_y = center_y - 5, center_y + 5
    padding_left = 0 if min_x > 0 else -min_x
    padding_right = 0 if max_x < board.size else max_x - board.size
    start_x = 0 if padding_left > 0 else min_x
    accessible_center_length = 9 - (padding_left + padding_right)
    for i, y in zip(range(9), range(min_y, max_y + 1)):
        if y < 0 or y >= board.size:
            # Inaccessible rows
            micro_board_symbols[i] = np.array(list(repeat(255, 9)))
        else:
            center_symbols = board.contents.symbols[y, start_x:start_x+accessible_center_length]
            # Accessible rows (not every column may be accessible)
            micro_board_symbols[i, 0:padding_left] = np.array(list(repeat(255, padding_left)))
            micro_board_symbols[i, padding_left:padding_left + accessible_center_length] = center_symbols
            micro_board_symbols[i, 9 - padding_right:9] = np.array(list(repeat(255, padding_right)))
    return micro_board_symbols


def transform_micro_board_into_neurons(micro_board):
    is_inaccessible = micro_board == 255
    is_invisible = micro_board == ord('#')
    is_numeric = (micro_board >= ord('0')) & (micro_board <= ord('9'))
    numeric_value = is_numeric * (micro_board - ord('0')) / 9.0
    values_accessible = is_inaccessible * 1.0 + is_invisible * 0.5
    neurons = np.ndarray((162,))
    neurons[0:81] = numeric_value.reshape((81,))
    neurons[81:162] = values_accessible.reshape((81,))
    return neurons


def get_evaluation_for_position(real_board, x, y):
    return real_board[x, y] != 'o'


def true_positions_iterator(empty_positions, size):
    i = 0
    for x in range(size):
        for y in range(size):
            if empty_positions[x, y]:
                yield x, y, i
                i += 1


def generate_input_for_board(board: Board, get_shape, iterator):
    empty_positions = board.contents.symbols == ord('#')
    shape = get_shape(empty_positions)
    input_values = np.ndarray(shape, np.float)
    for x, y, i in iterator(empty_positions, board.size):
        input_values[i] = transform_micro_board_into_neurons(get_micro_board(board, x, y))
    return input_values


def all_positions_iterator(_, size):
    i = 0
    for x in range(size):
        for y in range(size):
            yield x, y , i
            i += 1


def generate_input_for_every_field_in_board(board: Board):
    return generate_input_for_board(board, lambda a: (a.shape[0]**2, 162), generate_input_for_board)


def generate_output_for_boards(invisible_board):
    return (invisible_board != 'o') * 1.0


def get_possible_click_positions(game: Minesweeper):
    can_click = game.real_board != ord('o') & game.visible_board == ord('#')
    return true_positions_iterator(can_click, game.visible_board.size)


def get_possible_boards_on_every_empty_click(game: Minesweeper, symbols_list, values_list):
    is_empty = (game.real_board.contents.symbols == ord(EMPTY_SYMBOL)).transpose().reshape((81,))
    argmax = is_empty.argmax()
    added = 0
    while is_empty[argmax]:
        g = deepcopy(game)
        x = int(argmax % 9)
        y = int(argmax // 9)
        g.click(x, y)
        visible_symbols = g.visible_board.contents.symbols
        if not any(map(lambda v: (v == visible_symbols).all(), symbols_list)):
            symbols_list.append(visible_symbols)
            values_list.append(g.visible_board.contents.values)
            added += 1
        is_empty[argmax] = False
        argmax = is_empty.argmax()
    return added


def find_possibilities_until_the_end(game: Minesweeper, symbols_list, values_list):
    get_possible_boards_on_every_empty_click(game, symbols_list, values_list)
    for symbols, values in zip(symbols_list, values_list):
        g = Minesweeper(deepcopy(game.real_board))
        g.visible_board.contents.symbols = symbols
        g.visible_board.contents.values = values
        get_possible_boards_on_every_empty_click(g, symbols_list, values_list)
    return symbols_list, values_list


def generate_for_real_board(real_board):
    game = Minesweeper(real_board)
    symbols_list = []
    values_list = []
    find_possibilities_until_the_end(game, symbols_list, values_list)
    real_board_symbols = real_board.contents.symbols
    number_of_samples = min(len(symbols_list), len(values_list))
    repeated_real_board_symbols = repeat(real_board_symbols, number_of_samples)
    return symbols_list, repeated_real_board_symbols\


def generate_x_and_y_vals(iterable):
    for visible_symbols, values, invisible_symbols in iterable:
        # x_value = transform_input_board(visible_symbols, values)
        # y_value = create_output_board(visible_symbols, invisible_symbols)
        yield 0, 0


def generate_for_params(params_iterator, stop_after_sample):
    x_vals = np.ndarray((stop_after_sample, 162), np.float)
    y_vals = np.ndarray((stop_after_sample, 81), np.float)
    samples = 0
    for params in params_iterator:
        size = params[0]
        mines = params[1]
        b = Board.generate(size, mines)
        for x_value, y_value in generate_x_and_y_vals(generate_for_real_board(b)):
            if samples >= stop_after_sample:
                return x_vals, y_vals
            x_vals[samples] = x_value
            y_vals[samples] = y_value
            samples += 1
    return x_vals, y_vals
