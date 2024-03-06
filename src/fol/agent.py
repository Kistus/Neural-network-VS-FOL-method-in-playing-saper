from threading import Thread
import time
from tkinter import Button
import fol.utils
from fol.utils import get_predicate, FOL, execute_every_predicate3
from copy import deepcopy
import random


def get_moves_of_player(board):
    field_can_be_clicked = get_predicate('field_can_be_clicked', board)
    field_can_be_flagged = get_predicate('field_can_be_flagged', board)
    clicked_positions = []
    flagged_positions = []
    for position in board.get_every_position():
        if field_can_be_clicked(position):
            clicked_positions.append(position)
        elif field_can_be_flagged(position):
            flagged_positions.append(position)
    return clicked_positions, flagged_positions


def random_move_needed(player_moves):
    clicked_positions = player_moves[0]
    flagged_positions = player_moves[1]
    return len(clicked_positions) == 0 and len(flagged_positions) == 0


def get_random_move(board):
    field_can_be_randomly_selected = get_predicate(
        'field_can_be_randomly_selected', board)
    positions = list(filter(field_can_be_randomly_selected,
                     board.get_every_position()))
    if len(positions) == 0:
        field_invisible = get_predicate('field_invisible', board)
        positions = list(filter(field_invisible, board.get_every_position()))
    return random.choice(positions)


def solve_minesweeper(minesweeper):
    last_move = 'random'
    moves_taken = 0
    while not minesweeper.ended:
        clicked_positions, flagged_positions = get_moves_of_player(
            minesweeper.visible_board)
        if random_move_needed((clicked_positions, flagged_positions)):
            random_move = get_random_move(minesweeper.visible_board)
            last_move = 'random'
            moves_taken += 1
            minesweeper.click(random_move[0], random_move[1])
        else:
            for position in clicked_positions:
                moves_taken += 1
                last_move = 'calculated'
                minesweeper.click(position[0], position[1])
                if minesweeper.lost:
                    break
            for position in flagged_positions:
                last_move = 'calculated'
                minesweeper.set_flag(position[0], position[1])
    return last_move, moves_taken


def solver2(minesweeper, list_of_neighbour_lists, list_of_every_positions, graf):
    while not minesweeper.ended:
        f = FOL(minesweeper.visible_board,
                list_of_neighbour_lists, list_of_every_positions)
        execute_every_predicate3(f)

        if f.count_satisfying('field_can_be_clicked') > 0:
            for position in f.get_every_satisfying('field_can_be_clicked'):
                graf.clickOn(position[0], position[1])
                minesweeper.click(position[0], position[1])
        elif f.count_satisfying('field_can_be_randomly_selected') > 0:
            position = f.get_random_satisfying(
                'field_can_be_randomly_selected')
            graf.clickOn(position[0], position[1])
            minesweeper.click(position[0], position[1])
        elif not minesweeper.ended:
            position = f.get_random_satisfying('field_invisible')
            graf.clickOn(position[0], position[1])
            minesweeper.click(position[0], position[1])
        time.sleep(0.1)

    return minesweeper.won
