import sys
import itertools
from enum import IntEnum
from fol.utils import predicates, is_predicate_simple, \
    get_directly_implied_predicate_names, generate_every_position_list, generate_list_of_neighbour_lists
import numpy as np


def get_required_predicates(predicate_name):
    found_predicates = set()
    last_values = get_directly_implied_predicate_names(predicate_name)
    while len(last_values) > 0:
        new_version_of_last_values = []
        for value in last_values:
            if value not in found_predicates:
                found_predicates.add(value)
                new_version_of_last_values.extend(get_directly_implied_predicate_names(value))
        last_values = new_version_of_last_values
    if predicate_name in found_predicates:
        raise Exception('Predicate recursion is not allowed')
    return found_predicates


def is_or_predicate(predicate_name):
    return set(predicates[predicate_name].keys()) == {'name', 'satisfied_or'}


def is_and_predicate(predicate_name):
    return set(predicates[predicate_name].keys()) == {'name', 'satisfied_and'}


def is_simple_predicate(predicate_name):
    return \
        set(predicates[predicate_name].keys())\
        .issubset({'name', 'field_symbol', 'field_value_equal', 'field_value_not_equal'}) and \
        len(predicates[predicate_name].keys()) == 2


def get_requirement_accessor(predicate_name):
    requires_accessor_name = predicates[predicate_name].get('requires')
    if requires_accessor_name is None or type(requires_accessor_name) is not str:
        raise Exception(
            f'Predicate {predicate_name} have to have requires field containing a valid predicate expression')
    return PredicateAccessor(requires_accessor_name)


def is_neighbour_exists_predicate(predicate_name):
    key_names = set(predicates[predicate_name].keys())
    if 'requires' in key_names:
        key_names.remove('requires')
    return key_names == {'name', 'satisfied_neighbour_exists'}


def is_neighbours_satisfy_predicate(predicate_name):
    key_names = set(predicates[predicate_name].keys())
    if 'requires' in key_names:
        key_names.remove('requires')
    return key_names == {'name', 'neighbours_satisfy'}


def get_predicate_evaluation_order(predicate_name):
    required_predicates = get_required_predicates(predicate_name)
    requirements_for_each_one = {}
    for requirement_name in required_predicates:
        requirements_for_each_one[requirement_name] = get_required_predicates(requirement_name)
    evaluation_order = []
    evaluation_order_set = set()
    while len(required_predicates) > 0:
        to_remove = set()
        for requirement_name in required_predicates:
            if requirements_for_each_one[requirement_name].issubset(evaluation_order_set):
                evaluation_order.append(requirement_name)
                evaluation_order_set.add(requirement_name)
                to_remove.add(requirement_name)
        required_predicates = required_predicates.difference(to_remove)
    return evaluation_order


class PredicateAccessor:

    def __init__(self, name):
        if name[0] == '!':
            self.name = name[1:]
            self.negated = True
        else:
            self.name = name
            self.negated = False

    def access(self, values_set):
        predicate_value = values_set[self.name]
        if self.negated:
            predicate_value = ~predicate_value
        return predicate_value


def get_predicate_accessors(name_list):
    return list(map(PredicateAccessor, name_list))


class PredicateEvaluationResult:

    def __init__(self, values, all_positions):
        self._values = values
        self._all_positions = all_positions

    @property
    def satisfied_positions(self):
        for position in self._all_positions:
            if self._values[position]:
                yield position

    @property
    def random_satisfied_position(self):
        counted = len(self)
        idx = np.random.randint(0, counted)
        return itertools.islice(self.satisfied_positions, idx, idx+1).__next__()

    def __len__(self):
        return self._values.sum()


class PredicateType(IntEnum):

    NONE = 0
    SIMPLE_PREDICATE = 1
    OR_PREDICATE = 2
    AND_PREDICATE = 4
    NEIGHBOUR_EXISTS_PREDICATE = 8
    NEIGHBOURS_SATISFY_PREDICATE = 16

    NEIGHBOUR_COUNTING = 32
    NEIGHBOUR_COUNTING_DISABLED = 31

    SIMPLE_PREDICATE_WITH_NEIGHBOUR_COUNTING = 33
    OR_PREDICATE_WITH_NEIGHBOUR_COUNTING = 34
    AND_PREDICATE_WITH_NEIGHBOUR_COUNTING = 35
    NEIGHBOUR_EXISTS_WITH_NEIGHBOUR_COUNTING = 40
    NEIGHBOURS_SATISFY_WITH_NEIGHBOUR_COUNTING = 48

    def requires_neighbour_counting(self):
        return self.value & PredicateType.NEIGHBOUR_COUNTING


# TODO predicate execution (neighbour counting), without dependency checking
# TODO predicate execution with changes matrix + changes variable
# TODO predicate execution with


class BasePredicateEvaluator:

    predicate_names = set()
    simple_predicates = {}
    and_predicates = {}
    or_predicates = {}
    neighbour_exists_predicates = {}
    neighbours_satisfy_predicates = {}
    predicates = {}
    order_of_execution = {}
    checked_changes = {}

    def __init__(self, size):
        self.shape = (size, size)
        self.size = size
        self.list_of_every_positions = generate_every_position_list(size)
        self.list_of_every_neighbours = generate_list_of_neighbour_lists(size)
        self.predicate_values = {}
        self.board_contents = np.zeros(self.shape, np.byte)
        self.board_values = np.zeros(self.shape, np.byte)
        self.changed = np.ones(self.shape, np.bool)
        self.neighbour_counting_values = {}
        self.simple_predicate_checking_value = {}
        self.simple_predicate_value_or_symbol = {}
        self.simple_predicate_negate = {}
        for predicate_name in self.predicate_names:
            self.predicate_values[predicate_name] = np.zeros(self.shape, np.bool)
            self.neighbour_counting_values[predicate_name] = np.zeros(self.shape, np.byte)

    def update_board(self, board_contents, board_values):
        changed_contents = self.board_contents != board_contents
        changed_values = self.board_values != board_values
        self.board_contents = np.copy(board_contents)
        self.board_values = np.copy(board_values)
        self.changed = changed_contents | changed_values
        for key in self.checked_changes.keys():
            self.checked_changes[key] = False

    def _execute_predicate(self, predicate_name):
        for predicate in self.order_of_execution[predicate_name]:
            self._execute_predicate_without_dependency_check(predicate)
        self._execute_predicate_without_dependency_check(predicate_name)

    def _execute_predicate_without_dependency_check(self, predicate_name):
        if not self.checked_changes[predicate_name]:
            self._execute_predicate_without_checking_changes(predicate_name)
            self.checked_changes[predicate_name] = True

    def _execute_predicate_without_checking_changes(self, predicate_name):
        predicate_type = self.predicates[predicate_name]
        neighbour_counting = predicate_type & PredicateType.NEIGHBOUR_COUNTING
        predicate_type_without_neighbour_counting = \
            PredicateType(predicate_type & PredicateType.NEIGHBOUR_COUNTING_DISABLED)
        method_match = {
            PredicateType.SIMPLE_PREDICATE: self._execute_simple_predicate,
            PredicateType.OR_PREDICATE: self._perform_or_predicate,
            PredicateType.AND_PREDICATE: self._perform_and_predicate,
            PredicateType.NEIGHBOUR_EXISTS_PREDICATE: self._perform_neighbour_exists_predicate,
            PredicateType.NEIGHBOURS_SATISFY_PREDICATE: self._perform_neighbours_satisfy_predicate
        }[predicate_type_without_neighbour_counting]
        new_values = method_match(predicate_name)
        if neighbour_counting:
            self._neighbour_counting(predicate_name, new_values)
        self.predicate_values[predicate_name] = new_values

    def _get_neighbours(self, pos):
        return self.list_of_every_neighbours[pos[1] * self.size + pos[0]]

    def _neighbour_counting(self, predicate_name, new_values):
        changed = self.predicate_values[predicate_name] != new_values
        is_one = new_values == 1
        changed_from_zero_to_one = changed & is_one
        changed_from_one_to_zero = changed & ~is_one
        neighbour_changes = np.zeros(self.shape, np.bool)
        neighbour_counting_values = self.neighbour_counting_values[predicate_name]
        for position in self.list_of_every_positions:
            if changed_from_zero_to_one[position]:
                for neighbour in self._get_neighbours(position):
                    neighbour_counting_values[neighbour] += 1
                    neighbour_changes[neighbour] = True
            elif changed_from_one_to_zero[position]:
                for neighbour in self._get_neighbours(position):
                    neighbour_counting_values[neighbour] -= 1
                    neighbour_changes[neighbour] = True
        return neighbour_changes | changed

    def _execute_simple_predicates(self):
        changes = np.zeros(self.shape, np.bytes)
        for predicate_name in self.simple_predicates.keys():
            changes |= self._execute_simple_predicate(predicate_name)
        return changes

    def _execute_simple_predicate(self, predicate_name):
        specification = self.simple_predicates[predicate_name]
        checking_value = specification[0]
        is_symbol_based = specification[1]
        is_negated = specification[2]
        predicate_values = None
        if is_symbol_based:
            predicate_values = self.board_contents == checking_value
        else:
            predicate_values = self.board_values == checking_value

        if is_negated:
            predicate_values = ~predicate_values

        return predicate_values

    def _check_neighbour_existence(self, predicate_name):
        return self.neighbour_counting_values[predicate_name] > 0

    def _check_neighbour_satisfaction(self, predicate_name):
        return self.neighbour_counting_values[predicate_name] == self.board_values

    def _perform_and_predicate(self, predicate_name):
        return self._perform_and_or_predicate(predicate_name, self.and_predicates, lambda v0, v1: v0 & v1)

    def _perform_or_predicate(self, predicate_name):
        return self._perform_and_or_predicate(predicate_name, self.or_predicates, lambda v0, v1: v0 | v1)

    def _perform_and_or_predicate(self, predicate_name, and_or_predicates, operation):
        accessors = and_or_predicates[predicate_name]
        value = accessors[0].access(self.predicate_values)
        for accessor in accessors[1:]:
            value = operation(value, accessor.access(self.predicate_values))
        return value

    def _perform_neighbour_exists_predicate(self, predicate_name):
        predicate_spec = self.neighbour_exists_predicates[predicate_name]
        requirement_accessor = predicate_spec[0]
        neighbour_counting_name = predicate_spec[1]
        result = self._check_neighbour_existence(neighbour_counting_name)
        result &= requirement_accessor.access(self.predicate_values)
        return result

    def _perform_neighbours_satisfy_predicate(self, predicate_name):
        predicate_spec = self.neighbours_satisfy_predicates[predicate_name]
        requirement_accessor = predicate_spec[0]
        neighbour_counting_name = predicate_spec[1]
        result = self._check_neighbour_satisfaction(neighbour_counting_name)
        result &= requirement_accessor.access(self.predicate_values)
        return result


def compile_predicates():
    compiled_predicates = {}
    simple_predicates = {}
    and_predicates = {}
    or_predicates = {}
    neighbours_satisfy_predicates = {}
    neighbour_exists_predicates = {}
    neighbour_counting_predicates = set()
    predicate_types = {}
    order_of_execution = {}
    checked_changes = {}

    for predicate_name in predicates.keys():

        order_of_execution[predicate_name] = get_predicate_evaluation_order(predicate_name)
        checked_changes[predicate_name] = False

        def make_predicate(name):
            def predicate(self):
                self._execute_predicate(name)
                return PredicateEvaluationResult(self.predicate_values[name], self.list_of_every_positions)
            return predicate

        compiled_predicates['predicate_' + predicate_name] = make_predicate(predicate_name)
        if is_simple_predicate(predicate_name):
            is_symbol_based = predicates[predicate_name].get('field_symbol') is not None
            checking_value = 0
            is_negated = False
            if is_symbol_based:
                checking_value = np.byte(ord(predicates[predicate_name]['field_symbol']))
            elif predicates[predicate_name].get('field_value_equal') is not None:
                checking_value = np.byte(predicates[predicate_name].get('field_value_equal'))
            elif predicates[predicate_name].get('field_value_not_equal') is not None:
                checking_value = np.byte(predicates[predicate_name].get('field_value_not_equal'))
                is_negated = True
            simple_predicates[predicate_name] = \
                (checking_value, is_symbol_based, is_negated)
            predicate_types[predicate_name] = PredicateType.SIMPLE_PREDICATE
        elif is_and_predicate(predicate_name):
            and_predicates[predicate_name] = get_predicate_accessors(predicates[predicate_name].get('satisfied_and'))
            predicate_types[predicate_name] = PredicateType.AND_PREDICATE
        elif is_or_predicate(predicate_name):
            or_predicates[predicate_name] = get_predicate_accessors(predicates[predicate_name].get('satisfied_or'))
            predicate_types[predicate_name] = PredicateType.OR_PREDICATE
        elif is_neighbour_exists_predicate(predicate_name):
            neighbour_counting_predicate = predicates[predicate_name]['satisfied_neighbour_exists']
            neighbour_exists_predicates[predicate_name] = \
                (get_requirement_accessor(predicate_name), neighbour_counting_predicate)
            neighbour_counting_predicates.add(neighbour_counting_predicate)
            predicate_types[predicate_name] = PredicateType.NEIGHBOUR_EXISTS_PREDICATE
        elif is_neighbours_satisfy_predicate(predicate_name):
            neighbour_counting_predicate = predicates[predicate_name]['neighbours_satisfy']
            neighbours_satisfy_predicates[predicate_name] = \
                (get_requirement_accessor(predicate_name), neighbour_counting_predicate)
            neighbour_counting_predicates.add(neighbour_counting_predicate)
            predicate_types[predicate_name] = PredicateType.NEIGHBOURS_SATISFY_PREDICATE
        else:
            raise Exception(f'Predicate {predicate_name} is does not belong to any of the supported predicate classes')

    difference = neighbour_counting_predicates.difference(set(predicates.keys()))
    if len(difference) > 0:
        for element in difference:
            raise Exception(f'There is no predicate with name {element}')

    for name in neighbour_counting_predicates:
        predicate_types[name] = PredicateType(predicate_types[name] | PredicateType.NEIGHBOUR_COUNTING)

    compiled_predicates['predicates'] = predicate_types
    compiled_predicates['and_predicates'] = and_predicates
    compiled_predicates['or_predicates'] = or_predicates
    compiled_predicates['predicate_names'] = set(predicates.keys())
    compiled_predicates['simple_predicates'] = simple_predicates
    compiled_predicates['neighbour_exists_predicates'] = neighbour_exists_predicates
    compiled_predicates['neighbours_satisfy_predicates'] = neighbours_satisfy_predicates
    compiled_predicates['order_of_execution'] = order_of_execution
    compiled_predicates['checked_changes'] = checked_changes
    return type('PredicateEvaluator', (BasePredicateEvaluator, ), compiled_predicates)
