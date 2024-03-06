from board import Board
from symbols import MINE_SYMBOL


def positive_int(val):
    x = int(val)
    if x <= 0:
        raise ValueError(f'Value {val} should be positive')
    return x


def board_validate(board: Board):
    if board.size != board.contents.size:
        raise ValueError('Board invalid')

    mines = 0
    for x in range(board.size):
        for y in range(board.size):
            if board[x, y] == MINE_SYMBOL:
                mines += 1
    if mines != board.mines:
        raise ValueError('Board invalid')
