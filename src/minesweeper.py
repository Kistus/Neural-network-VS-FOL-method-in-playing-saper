from board import Board
from symbols import *


class Minesweeper:
    mine_symbol = MINE_SYMBOL
    flag_symbol = FLAG_SYMBOL
    empty_symbol = EMPTY_SYMBOL
    closed_symbol = CLOSED_SYMBOL

    def __init__(self, real_board: Board):
        size = real_board.size
        mines = real_board.mines
        self.cols = size
        self.rows = size
        self.mines = mines
        self.visible_board = Board(size, self.closed_symbol)  # The board visible by the player
        self.visible_board.mines = mines
        self.real_board = real_board  # The board with the game contents
        self.flagged_correctly = 0
        self.flagged_incorrectly = 0
        self.lost = False
        self.won = False
        self.ended = False

    def print_closed_board(self):
        print(self.visible_board.contents)

    def set_flag(self, x, y):
        if self.visible_board[x, y] != self.closed_symbol:
            return self.visible_board
        self.visible_board[x, y] = self.flag_symbol
        if self.real_board[x, y] == self.mine_symbol:
            self.flagged_correctly += 1
        else:
            self.flagged_incorrectly += 1
        return self.visible_board

    def unset_flag(self, x, y):
        if self.visible_board[x, y] != self.flag_symbol:
            return self.visible_board
        if self.real_board[x, y] == self.mine_symbol:
            self.flagged_correctly -= 1
        else:
            self.flagged_incorrectly -= 1
        self.visible_board[x, y] = self.empty_symbol
        return self.visible_board

    def cascade_open(self, x, y):

        def simple_cascade(pos):
            if self.visible_board[pos] != self.real_board[pos]:
                self.visible_board[pos] = self.real_board[pos]
                if self.real_board[pos] == self.empty_symbol:
                    self.cascade_open(pos[0], pos[1])

        positions = [
            (x - 1, y - 1),
            (x, y - 1),
            (x + 1, y - 1),
            (x + 1, y),
            (x + 1, y + 1),
            (x, y + 1),
            (x - 1, y + 1),
            (x - 1, y)
        ]

        for position in positions:
            try:
                simple_cascade(position)
            except ValueError:
                continue

    def click(self, x, y):
        current_symbol = self.real_board[x, y]
        self.visible_board[x, y] = current_symbol
        if current_symbol == self.mine_symbol:
            self.lost = True
            self.ended = True
            self.handle_lose()
        elif current_symbol == self.empty_symbol:
            self.cascade_open(x, y)
        if self.game_won():
            self.won = True
            self.ended = True
            self.handle_win()
        return self.visible_board

    def game_won(self):
        """
                Game is won only when all of these statements are true:
                1. The player didn't click on a mine
                2. The player didn't flag a field with no mine
                3. The number of not flagged mines equals the number of invisible elements
        """
        if self.lost:
            return False
        if self.flagged_incorrectly != 0:
            return False
        elements = self.rows * self.cols
        elements_left = elements - self.visible_board.filled_elements
        mines_left = self.mines - self.flagged_correctly
        return elements_left == mines_left

    def handle_lose(self):
        pass

    def handle_win(self):
        pass
