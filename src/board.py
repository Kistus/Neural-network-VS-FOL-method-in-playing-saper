import numpy as np
import random
from symbols import EMPTY_SYMBOL as EMPTY_VALUE
from symbols import MINE_SYMBOL

"""
    String value (one character) that represents empty element of board.
"""
VALID_ROW_VALUES = [' ', 'o', '1', '2', '3', '4', '5', '6', '7', '8']
"""
    Represents the only valid row values.
"""


class BoardContents:

    def __init__(self, size, initialize=True, initialized_value=EMPTY_VALUE):
        self.size = size
        self.filled_elements = 0
        self.initialized_value = initialized_value
        shape = (size, size)
        self.symbols = np.ndarray(shape, np.byte)
        self.values = np.ndarray(shape, np.byte)
        self.changed_positions = []
        if initialize:
            self._rows = [
                [initialized_value for _ in range(size)] for _ in range(size)]
            number_value = 0
            if initialized_value.isnumeric():
                val = int(initialized_value)
                number_value = val
            ord_val = ord(initialized_value)
            for x in range(size):
                for y in range(size):
                    self.symbols[x, y] = ord_val
                    self.values[x, y] = number_value

    def __str__(self):
        contents = ''
        for row in range(self.size):
            for column in range(self.size):
                contents += self._rows[row][column]
            contents += '\n'
        return contents

    def __getitem__(self, item):
        self._validate_key(item)
        return self._rows[item[1]][item[0]]

    def __setitem__(self, key, item):
        self._validate_key(key)
        column = key[0]
        row = key[1]
        self.changed_positions.append(key)
        if item.isnumeric():
            self.values[column, row] = int(item)
        else:
            self.values[column, row] = 0
        self.symbols[column, row] = ord(item)
        if self[key] == self.initialized_value and item != self.initialized_value:
            self.filled_elements += 1
        self._rows[row][column] = item
        return True

    def _validate_part_of_key(self, part):
        if type(part) is not int:
            raise ValueError('Key must contain integers')
        if part < 0 or part >= self.size:
            raise ValueError(
                'Every integer of the key must be in range 0..size')

    def _validate_key(self, key):
        if type(key) is not tuple and len(key) != 2:
            raise ValueError('Key must be a tuple with two points')
        self._validate_part_of_key(key[0])
        self._validate_part_of_key(key[1])

    @classmethod
    def from_row_list(cls, row_list):
        size = len(row_list)
        contents = BoardContents(size, False)
        contents._rows = []
        filled_elements = 0
        for row in row_list:
            columns = list(row)
            if len(row) != size:
                raise ValueError('List of rows is invalid')
            valid_elements = 0
            for valid_value in VALID_ROW_VALUES:
                valid_elements += columns.count(valid_value)
            for value in columns:
                if value != EMPTY_VALUE:
                    filled_elements += 1
            if valid_elements != size:
                raise ValueError('List of rows is invalid')

            contents._rows.append(columns)
        contents.filled_elements = filled_elements
        return contents

    @classmethod
    def generate(cls, size, mines):
        rows = size
        cols = size

        board = [[0 for _ in range(0, rows)] for _ in range(0, cols)]

        board_coordinates = [(x, y) for x in range(0, cols)
                             for y in range(0, rows)]
        mine_coordinates = random.sample(board_coordinates, mines)

        for mine in mine_coordinates:
            x, y = mine
            board[x][y] = MINE_SYMBOL
            neighbors = [(x - 1, y), (x - 1, y + 1), (x, y - 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1), (x, y + 1),
                         (x - 1, y - 1)]
            for n in neighbors:
                if 0 <= n[0] <= cols - 1 and 0 <= n[1] <= rows - 1 and n not in mine_coordinates:
                    board[n[0]][n[1]] += 1

        filled_elements = 0
        board_contents = BoardContents(size, False)

        for i in range(rows):
            for j in range(cols):
                if board[i][j] == 0:
                    board[i][j] = EMPTY_VALUE
                    board_contents.values[j, i] = 0
                    board_contents.symbols[j, i] = ord(EMPTY_VALUE)
                else:
                    board[i][j] = str(board[i][j])
                    filled_elements += 1
                    board_contents.symbols[j, i] = ord(board[i][j])
                    if board[i][j].isnumeric():
                        board_contents.values[j, i] = int(board[i][j])
                    else:
                        board_contents.values[j, i] = 0

        board_contents._rows = board
        board_contents.filled_elements = filled_elements
        return board_contents


class Board:

    def __init__(self, size=None, initialized_value=EMPTY_VALUE):
        if size is not None:
            self.size = size
            self.contents = BoardContents(size, True, initialized_value)

    def __getitem__(self, item):
        return self.contents[item]

    def __setitem__(self, key, value):
        return self.contents.__setitem__(key, value)

    @property
    def filled_elements(self):
        return self.contents.filled_elements

    @property
    def changed_positions(self):
        return self.contents.changed_positions

    def remove_changed_positions(self):
        self.contents.changed_positions = []

    @classmethod
    def generate(cls, size, mines):
        board = Board()
        contents = BoardContents.generate(size, mines)
        board.size = size
        board.mines = mines
        board.contents = contents
        return board

    def get_every_position(self):
        for x in range(self.size):
            for y in range(self.size):
                yield x, y
