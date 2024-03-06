from fol.utils import predicate
from symbols import CLOSED_SYMBOL, FLAG_SYMBOL

predicate(name='field_contain_number', field_value_not_equal=0)
predicate(name='field_invisible', field_symbol=CLOSED_SYMBOL)
predicate(name='field_flagged', field_symbol=FLAG_SYMBOL)
predicate(name='field_invisible_or_contain_flag', satisfied_or=['field_flagged', 'field_invisible'])
predicate(name='field_interesting', requires='field_invisible', satisfied_neighbour_exists='field_contain_number')
predicate(name='are_bomb_positions_obvious', requires='field_contain_number',
          neighbours_satisfy='field_invisible_or_contain_flag')
predicate(name='field_contain_bomb', requires='field_interesting',
          satisfied_neighbour_exists='are_bomb_positions_obvious')
predicate(name='field_flagged_or_contain_bomb', satisfied_or=['field_flagged', 'field_contain_bomb'])
predicate(name='flagged_necessary_neighbours', requires='field_contain_number',
          neighbours_satisfy='field_flagged_or_contain_bomb')
predicate(name='field_may_be_clicked',
          requires='field_interesting', satisfied_neighbour_exists='flagged_necessary_neighbours')
predicate(name='field_can_be_clicked', satisfied_and=['field_may_be_clicked', '!field_contain_bomb'])
predicate(name='field_can_be_flagged', satisfied_and=['field_interesting', 'field_contain_bomb'])
predicate(name='field_can_be_randomly_selected', satisfied_and=['field_invisible', '!field_interesting'])
