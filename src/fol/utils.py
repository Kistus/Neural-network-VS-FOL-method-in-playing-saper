from functools import reduce, partial
from collections import namedtuple
from board import Board
import numpy as np
import itertools

BinaryClassification = namedtuple('Classification', 'positive negative')

predicates = {}


def number_outside_bounds(number, lower_bound, higher_bound):
    return number < lower_bound or number >= higher_bound


def field_exists(board, position):
    x = position[0]
    y = position[1]
    field_not_exists = number_outside_bounds(x, 0, board.size)
    field_not_exists |= number_outside_bounds(y, 0, board.size)
    return not field_not_exists


def get_neighbours(board, point):
    x = point[0]
    y = point[1]
    positions = (
        (x-1, y-1),
        (x-1, y),
        (x-1, y+1),
        (x, y-1),
        (x+1, y-1),
        (x+1, y),
        (x+1, y+1),
        (x, y+1)
    )
    for position in positions:
        if position[0] < 0 or position[1] < 0:
            continue
        if position[0] >= board.size or position[1] >= board.size:
            continue
        yield position


def get_positions_that_changed(b0, b1, every_position, include_neighbours=False):
    for pos in every_position:
        if b0[pos] != b1[pos]:
            yield pos


def get_positions_that_changed_with_neighbours(fol, b0, b1, every_position):
    changed_positions = np.zeros(fol.shape, np.bool)
    for pos in every_position:
        if b0[pos] != b1[pos]:
            changed_positions[pos] = True
    true_values = np.ones(fol.shape, np.bool)
    neighbour_positions = reversed_neighbour_counting(fol, true_values, changed_positions)
    all_positions = changed_positions | neighbour_positions
    for pos in every_position:
        if all_positions[pos]:
            yield pos


def binary_classification(positions, predicate):
    def reducer(accum, curr):
        if predicate(curr):
            return BinaryClassification(accum.positive + 1, accum.negative)
        else:
            return BinaryClassification(accum.positive, accum.negative + 1)
    return reduce(reducer, positions, BinaryClassification(0, 0))


def predicate(**kwargs):
    name = kwargs.get('name')
    predicates[name] = kwargs


def predicate_from_evaluation(evaluation):
    def func(position):
        return evaluation[position]
    return func


def get_predicate(name, board):
    function = predicates.get(name)
    if function is not None:
        return partial(function, board)

    def always_false_predicate(pos):
        return False

    return always_false_predicate


def extend_board_with_logic(board):
    fol_info = type('FolBoard', (type(Board),), predicates)


def get_field_values(board):
    values = np.zeros((board.size, board.size), np.byte)
    for position in board.get_every_position():
        val = board[position]
        if val.isnumeric():
            values[position] = int(val)
    return values


def get_predicate_name(name):
    if name[0] == '!':
        return name[1:]
    else:
        return name


def get_directly_implied_predicate_names(name):
    predicate_name_getters = \
        ['requires', 'satisfied_and', 'satisfied_or', 'neighbours_satisfy', 'satisfied_neighbour_exists']
    names = []
    predicate_definition = predicates[name]
    for name_container in predicate_name_getters:
        value = predicate_definition.get(name_container)
        if value is not None:
            if type(value) is str:
                names.append(get_predicate_name(value))
            else:
                for name in value:
                    names.append(get_predicate_name(name))
    return names


def is_predicate_simple(name):
    predicate_name_getters = \
        ['requires', 'satisfied_and', 'satisfied_or', 'neighbours_satisfy', 'satisfied_neighbour_exists']
    predicate_definition = predicates[name]
    for name_container in predicate_name_getters:
        if predicate_definition.get(name_container) is not None:
            return False
    return True


def get_simple_predicate(name, shape):
    if is_predicate_simple(name):
        predicate_specification = predicates[name]
        field_symbol = predicate_specification.get('field_symbol')
        field_value_equal = predicate_specification.get('field_value_equal')
        field_value_not_equal = predicate_specification.get('field_value_not_equal')
        check_values = True
        equals_is_true = True
        checking_array = np.ndarray(shape, np.byte)
        value = 0
        if field_symbol is not None:
            check_values = False
            value = ord(field_symbol)
        else:
            if not (field_value_equal is not None or field_value_not_equal is not None):
                return None
            if field_value_not_equal is not None:
                equals_is_true = False
                value = field_value_not_equal
            else:
                value = field_value_equal
        for x in range(shape[0]):
            for y in range(shape[1]):
                checking_array[x, y] = value
        return checking_array, check_values, equals_is_true





def get_and_or_predicate(name):
    if not is_predicate_simple(name):
        predicate_specification = predicates[name]
        satisfied_or = predicate_specification.get('satisfied_or')
        satisfied_and = predicate_specification.get('satisfied_and')
        if not (satisfied_or is None or satisfied_and is None):
            return None


class Element:

    def __init__(self, name):
        if name[0] == '!':
            self.negated = True
            self.name = name[1:]
        else:
            self.negated = False
            self.name = name

    def value(self, fol):
        return self.process(fol.predicate_values[self.name])

    def value_neighbour_counting(self, fol, operation):
        return self.process(operation(fol.neighbour_counting_values[self.name], fol.field_values))

    def process(self, value):
        if self.negated:
            return ~value
        else:
            return value


def to_element_list(elements):
    return list(map(Element, elements))


def get_and_or_predicate(name, satisfied_name, operation):
    specification = predicates[name]
    element_list = to_element_list(specification.get(satisfied_name))
    if len(element_list) == 0:
        def zeros(fol):
            return np.zeros(fol.shape, np.bool)
        return zeros

    def get_every_value(fol):
        current = element_list[0].value(fol)
        for element in element_list[1:]:
            current = operation(current, element.value(fol))
        return current

    return get_every_value


def get_or_predicate(name):
    return get_and_or_predicate(name, 'satisfied_or', lambda a, b: a | b)


def get_and_predicate(name):
    return get_and_or_predicate(name, 'satisfied_and', lambda a, b: a & b)


def get_neighbour_based_predicate(name, satisfying_name, operation):
    specs = predicates[name]
    satisfying_predicate = specs.get(satisfying_name)
    required_predicate = specs.get('requires')
    element = Element(satisfying_predicate)
    required = None
    if required_predicate is not None:
        required = Element(required_predicate)

        def pred_with_requirement(fol):
            values = element.value_neighbour_counting(fol, operation)
            return values & required.value(fol)
        return pred_with_requirement

    def pred(fol):
        values = element.value_neighbour_counting(fol, operation)
        return values

    return pred


def get_neighbour_exists_predicate(name):
    return get_neighbour_based_predicate(name, 'satisfied_neighbour_exists', lambda res, _: res > 0)


def get_neighbours_satisfy_predicate(name):
    return get_neighbour_based_predicate(name, 'neighbours_satisfy', lambda res, values: res == values)


def reversed_neighbour_counting(fol, required_predicate_values, neighbour_predicate_values):
    result = np.zeros(fol.shape, np.byte)
    for position in fol.list_of_every_positions:
        if required_predicate_values[position]:
            for neighbour in fol.get_neighbours(position):
                if neighbour_predicate_values[neighbour]:
                    result[position] += 1
    return result


class FOL:

    def __init__(self, board, list_of_neighbour_lists, list_of_every_positions):
        self.board = board
        self.field_values = board.contents.values
        self.shape = (board.size, board.size)
        self.size = board.size
        self.predicate_values = {}
        self.neighbour_counting_values = {}
        self.list_of_neighbour_lists = list_of_neighbour_lists
        self.list_of_every_positions = list_of_every_positions

    def get_neighbours(self, pos):
        return self.list_of_neighbour_lists[pos[1] * self.size + pos[0]]

    def perform_simple_predicate_with_neighbour_counting(self, simple_name):
        simple_predicate = get_simple_predicate(simple_name)
        predicate_values = np.zeros(self.shape, np.bool)
        neighbour_counting_values = np.zeros(self.shape, np.byte)
        for position in self.board.get_every_position():
            if simple_predicate(self, position):
                predicate_values[position] = 1
                for neighbour in get_neighbours(self.board, position):
                    neighbour_counting_values[neighbour] += 1
        self.predicate_values[simple_name] = predicate_values
        self.neighbour_counting_values[simple_name] = neighbour_counting_values

    def perform_simple_predicate(self, simple_name):
        checking_array, check_values, equals_is_true = get_simple_predicate(simple_name, self.shape)
        result = None
        if check_values:
            result = self.field_values == checking_array
        else:
            result = self.board.contents.symbols == checking_array
        if not equals_is_true:
            result = ~result
        self.predicate_values[simple_name] = result

    def neighbour_counting(self, simple_name):
        count = np.zeros(self.shape, np.byte)
        values = self.predicate_values[simple_name]
        for position in self.list_of_every_positions:
            if values[position]:
                for neighbour_pos in self.get_neighbours(position):
                    count[neighbour_pos] += 1
        self.neighbour_counting_values[simple_name] = count

    def count_satisfying(self, name):
        return self.predicate_values[name].sum()

    def get_every_satisfying(self, name):
        res = self.predicate_values[name]
        for position in self.list_of_every_positions:
            if res[position]:
                yield position

    def get_nth_satisfying(self, name, element):
        elements = self.get_every_satisfying(name)
        elements = itertools.islice(elements, element, element+1)
        return elements.__next__()

    def get_random_satisfying(self, name):
        counted = self.count_satisfying(name)
        n = np.random.randint(0, counted)
        return self.get_nth_satisfying(name, n)


def execute_every_predicate3(fol):
    fol.perform_simple_predicate('field_contain_number')
    fol.perform_simple_predicate('field_invisible')
    fol.perform_simple_predicate('field_flagged')
    fol.predicate_values['field_invisible_or_contain_flag'] = \
        get_or_predicate('field_invisible_or_contain_flag')(fol)
    fol.neighbour_counting_values['field_contain_number'] = \
        reversed_neighbour_counting(
            fol, fol.predicate_values['field_invisible'], fol.predicate_values['field_contain_number'])
    fol.predicate_values['field_interesting'] = \
        get_neighbour_exists_predicate('field_interesting')(fol)
    fol.neighbour_counting_values['field_invisible_or_contain_flag'] = \
        reversed_neighbour_counting(fol, fol.predicate_values['field_contain_number'],
                                fol.predicate_values['field_invisible_or_contain_flag'])
    fol.predicate_values['are_bomb_positions_obvious'] = \
        get_neighbours_satisfy_predicate('are_bomb_positions_obvious')(fol)
    fol.neighbour_counting_values['are_bomb_positions_obvious'] =\
        reversed_neighbour_counting(fol,
                                    fol.predicate_values['field_interesting'],
                                    fol.predicate_values['are_bomb_positions_obvious'])
    fol.predicate_values['field_contain_bomb'] = \
        get_neighbour_exists_predicate('field_contain_bomb')(fol)
    fol.predicate_values['field_flagged_or_contain_bomb'] = \
        get_or_predicate('field_flagged_or_contain_bomb')(fol)
    fol.neighbour_counting_values['field_flagged_or_contain_bomb'] = \
        reversed_neighbour_counting(fol, fol.predicate_values['field_contain_number'],
                                    fol.predicate_values['field_flagged_or_contain_bomb'])
    fol.predicate_values['flagged_necessary_neighbours'] = \
        get_neighbours_satisfy_predicate('flagged_necessary_neighbours')(fol)
    fol.neighbour_counting_values['flagged_necessary_neighbours'] = \
        reversed_neighbour_counting(fol, fol.predicate_values['field_interesting'],
                                    fol.predicate_values['flagged_necessary_neighbours'])
    fol.predicate_values['field_may_be_clicked'] = \
        get_neighbour_exists_predicate('field_may_be_clicked')(fol)
    fol.predicate_values['field_can_be_clicked'] = \
        get_and_predicate('field_can_be_clicked')(fol)
    fol.predicate_values['field_can_be_flagged'] = \
        get_and_predicate('field_can_be_flagged')(fol)
    fol.predicate_values['field_can_be_randomly_selected'] = \
        get_and_predicate('field_can_be_randomly_selected')(fol)


def generate_every_position_list(size):
    positions_list = []
    for i in range(size ** 2):
        y = i % size
        x = i // size
        positions_list.append((x, y))
    return positions_list


def generate_list_of_neighbour_lists(size):
    result = [None for _ in range(size**2)]
    b = Board(size)
    for x in range(size):
        for y in range(size):
            pos = size * y + x
            result[pos] = list(get_neighbours(b, (x, y)))
    return result
