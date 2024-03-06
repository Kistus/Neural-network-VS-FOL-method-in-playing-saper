from board import Board
from symbols import *

class Minesweeper:
    mine_symbol = MINE_SYMBOL
    flag_symbol = FLAG_SYMBOL
    empty_symbol = EMPTY_SYMBOL
    closed_symbol = CLOSED_SYMBOL

    def __init__(self, real_board: Board):
        self.size = real_board.size
        mines = real_board.mines
        self.cols = self.size
        self.rows = self.size
        self.mines = mines
        self.visible_board = Board(self.size, self.closed_symbol)
        self.visible_board.mines = mines
        self.real_board = real_board
        self.flagged_correctly = 0
        self.flagged_incorrectly = 0
        self.lost = False
        self.won = False
        self.ended = False
        self.click_count = 0

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
        self.click_count += 1
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
