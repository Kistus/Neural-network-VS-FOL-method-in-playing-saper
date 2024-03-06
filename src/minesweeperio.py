from board import Board, BoardContents
from validation import positive_int, board_validate

BOARD_CONTENTS_ATTRIBUTE = 'contents'
"""
    Attribute that contains BoardContents
"""
BOARD_ATTRIBUTES = {
    'size': positive_int,
    'mines': positive_int
}
"""
    Every board attribute other than board contents.
    The attribute is optional (for both input and output)
    The value should be a function / type that can take string input and produce output in desired type.
    If the value is incorrect then it is necessary to raise an Error or Exception.
"""
BOARD_VALIDATION_FUNCTION = board_validate
"""
    The function that check if the board from the file is valid.
    This function should communicate errors through exceptions/errors.
    If the value is None then there is no validation.
    This function should also perform postprocessing of an object if this is necessary.
"""


def write_board_to_file(board, filename):
    return write_boards_to_file([board], filename)


def read_board_from_file(filename):
    boards = read_boards_from_file(filename)
    if len(boards) != 1:
        raise ValueError('The file contains more than one minesweeper board')
    return boards[0]


def read_boards_from_file(filename):
    boards = []

    def validate_board(minesweeper_board):
        if BOARD_VALIDATION_FUNCTION is not None and BOARD_VALIDATION_FUNCTION is callable:
            BOARD_VALIDATION_FUNCTION(minesweeper_board)

    with open(filename, 'r') as f:
        rows = []
        board = Board()
        reading_attributes = True
        for line in f.readlines():
            line = line[:-1]
            if len(line) == 0:
                contents = BoardContents.from_row_list(rows)
                board.__setattr__(BOARD_CONTENTS_ATTRIBUTE, contents)
                validate_board(board)
                reading_attributes = True
                rows = []
                boards.append(board)
                board = Board()
                continue
            if reading_attributes:
                separator_pos = line.find(': ')
                if separator_pos == -1:
                    reading_attributes = False
                else:
                    attribute_name = line[:separator_pos]
                    attribute_value_str = line[separator_pos+2:]
                    if attribute_name in BOARD_ATTRIBUTES:
                        parser = BOARD_ATTRIBUTES.get(attribute_name)
                        attribute_value = parser(attribute_value_str)
                        board.__setattr__(attribute_name, attribute_value)
                    continue
            rows.append(line)
    return boards


def write_boards_to_file(boards, filename, append=False):
    if type(boards) is not list and len(boards) < 1:
        raise ValueError('Boards argument must contain a valid list with at least one element')
    for board in boards:
        if not isinstance(board, Board):
            raise ValueError('Every board must be a perfectly valid board object')
    mode = 'w'
    if append:
        mode = 'a'
    with open(filename, mode) as f:
        for board in boards:
            for attribute in BOARD_ATTRIBUTES:
                try:
                    value = board.__getattribute__(attribute)
                    escaped_value = str(value).replace('\n', '\\n')
                    f.write(f'{attribute}: {escaped_value}\n')
                except AttributeError:
                    pass
            contents = board.__getattribute__(BOARD_CONTENTS_ATTRIBUTE)
            f.write(str(contents))
            f.write('\n')
    return True
