import fol.predicates
import fol.interpreter
from copy import deepcopy
from board import Board
import numpy as np
from minesweeper import Minesweeper

PredicateEvaluator = fol.interpreter.compile_predicates()

SIZE = 9

def agent(evaluator, game: Minesweeper):
    while not game.ended:
        board = game.visible_board
        evaluator.update_board(board.contents.symbols, board.contents.values)
        result = evaluator.predicate_field_can_be_clicked()
        if len(result) > 0:
            for position in result.satisfied_positions:
                game.click(position[0], position[1])
        else:
            result = evaluator.predicate_field_can_be_randomly_selected()
            if len(result) == 0:
                result = evaluator.predicate_field_invisible()
            position = result.random_satisfied_position
            game.click(position[0], position[1])
    return game.won


def calculate_for_empty_game(evaluator):
    board = Board(evaluator.shape[0], '#')
    evaluator.update_board(board.contents.symbols, board.contents.values)
    evaluator.predicate_field_can_be_clicked()
    return np.copy(evaluator.neighbour_counting_values['field_invisible_or_contain_flag'])


NEIGHBOUR_COUNTING_SPECIAL = calculate_for_empty_game(PredicateEvaluator(SIZE))


def reset_evaluator_to_empty_game(evaluator):
    predicate_names = evaluator.predicate_values.keys()
    for name in predicate_names:
        evaluator.predicate_values[name] = np.zeros(evaluator.shape, np.bool)
        evaluator.neighbour_counting_values[name] = np.zeros(evaluator.shape, np.byte)
        evaluator.checked_changes[name] = True
    evaluator.predicate_values['field_invisible'] = np.ones(evaluator.shape, np.bool)
    evaluator.predicate_values['field_invisible_or_contain_flag'] = np.ones(evaluator.shape, np.bool)
    evaluator.neighbour_counting_values['field_invisible_or_contain_flag'] = np.copy(NEIGHBOUR_COUNTING_SPECIAL)


def test_multiple_games(n, size, mines):
    evaluator = PredicateEvaluator(size)
    empty_board = Board(size, '#')
    evaluator.update_board(empty_board.contents.symbols, empty_board.contents.values)
    evaluator.predicate_field_can_be_clicked()
    games_won = 0
    games_lost = 0
    for _ in range(n):
        board = Board.generate(size, mines)
        game = Minesweeper(board)
        if agent(evaluator, game):
            games_won += 1
        else:
            games_lost += 1
        reset_evaluator_to_empty_game(evaluator)
    print(
        f'During {n} tests on board of size {size} with {mines} mines FOL agent won {games_won}'
        f' and lost {games_lost} times')
#
#
# def nn_test_multiple_games(n, mines):
#     won = 0
#     lost = 0
#     for _ in range(n):
#         b = Board.generate(9, mines)
#         game = Minesweeper(b)
#         if neural_agent(game):
#             won += 1
#         else:
#             lost += 1
#     print(f'During {n} tests on 9x9 board neural network agent won {won} and lost {lost} times')
#

