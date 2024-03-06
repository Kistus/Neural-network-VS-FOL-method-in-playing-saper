from symbols import CLOSED_SYMBOL, MINE_SYMBOL, EMPTY_SYMBOL
from minesweeper import Minesweeper
from board import Board
import numpy as np
from itertools import repeat
from copy import deepcopy


def transform_input_board(board_contents: np.ndarray, board_values: np.ndarray):
    normalized_values = board_values / 9.0
    invisible = (board_contents == ord(CLOSED_SYMBOL)) / 1.0
    input_values = np.ndarray((162,))
    input_values[0:81] = normalized_values.transpose().reshape((81,))
    input_values[81:] = invisible.transpose().reshape((81,))
    return input_values


def create_output_board(input_board_contents, output_board_contents):
    may_be_clicked = input_board_contents != ord(CLOSED_SYMBOL)
    not_contain_bomb = output_board_contents != ord(MINE_SYMBOL)
    can_be_clicked = (may_be_clicked & not_contain_bomb) / 1.0
    return can_be_clicked.transpose().reshape((81,))


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
    return zip(symbols_list, values_list, repeated_real_board_symbols)


def generate_x_and_y_vals(iterable):
    for visible_symbols, values, invisible_symbols in iterable:
        x_value = transform_input_board(visible_symbols, values)
        y_value = create_output_board(visible_symbols, invisible_symbols)
        yield x_value, y_value


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
