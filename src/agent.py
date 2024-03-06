import predicates # It loads the predicates into memory
import numpy as np
from interpreter import compile_predicates
from board import Board


class Agent:

    def __init__(self, board_size):
        self.board_size = board_size
        predicate_evaluator = compile_predicates()
        self.evaluator = predicate_evaluator(board_size)
        empty_board = Board(board_size, '#')
        self.evaluator.update_board(empty_board.contents.symbols, empty_board.contents.values)
        self.last_move_random = True
        self.neighbour_counting_special = calculate_for_empty_game(self.evaluator)

    def solve(self, game):
        evaluator = self.evaluator
        self._reset_evaluator_to_empty_game(evaluator)
        while not game.ended:
            board = game.visible_board
            evaluator.update_board(board.contents.symbols, board.contents.values)
            result = evaluator.predicate_field_can_be_clicked()
            if len(result) > 0:
                for position in result.satisfied_positions:
                    game.click(position[0], position[1])
                    self.last_move_random = False
            else:
                result = evaluator.predicate_field_can_be_randomly_selected()
                if len(result) == 0:
                    result = evaluator.predicate_field_invisible()
                position = result.random_satisfied_position
                self.last_move_random = True
                game.click(position[0], position[1])

    def name(self):
        return 'fol'

    def _reset_evaluator_to_empty_game(self, evaluator):
        predicate_names = evaluator.predicate_values.keys()
        for name in predicate_names:
            evaluator.predicate_values[name] = np.zeros(evaluator.shape, bool)
            evaluator.neighbour_counting_values[name] = np.zeros(evaluator.shape, np.byte)
            evaluator.checked_changes[name] = True
        evaluator.predicate_values['field_invisible'] = np.ones(evaluator.shape, bool)
        evaluator.predicate_values['field_invisible_or_contain_flag'] = np.ones(evaluator.shape, bool)
        evaluator.neighbour_counting_values['field_invisible_or_contain_flag'] = np.copy(self.neighbour_counting_special)


def calculate_for_empty_game(evaluator):
    board = Board(evaluator.shape[0], '#')
    evaluator.update_board(board.contents.symbols, board.contents.values)
    evaluator.predicate_field_can_be_clicked()
    return np.copy(evaluator.neighbour_counting_values['field_invisible_or_contain_flag'])
