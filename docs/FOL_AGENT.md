# FOL Agent Predicates

## Request for comments


### Podstawowe predykaty do wykonania agenta

1. Czy pole jest warte uwagi (istnieje możliwość stwierdzenia z pewnością, czy jest tam bomba czy nie)

intresting(board, position)

Interesujące pole to takie, które spełnia 2 warunki jednocześnie:
- Jest zakryte (nie wiadomo co na nim jest)
- Posiada przynajmniej jednego sąsiada, którym jest liczba (z dowolnej strony)

W ten sposób eliminujemy pola o których nie możemy kompletnie nic powiedzieć, zostawiając przy tym pola jednoznaczne i niejednoznaczne.

2. Czy pole zawiera liczbę?

contain_number(board, position)

3. Czy bomby w okolicy mają oczywiste pozycje?

can_flag_bombs_around(board, position)

Liczba sąsiadów z niewidocznym elementem lub posiadających flagę = Liczba bomb (podana na danym polu)
W przypadku pól nie zawierających liczby daje fałsz. 

W ten sposób wiemy, że każdy z jego sąsiadów może być oflagowany.

4. Czy każdy nieoflagowany pusty sąsiad jest bombą?

not_flagged_neighbours_contain_bombs(board, position)

Liczba bomb (pokazana na elemencie planszy) = Liczba oflagowanych pól sąsiadów (tylko gdy przejdzie się contain_number(board, position))

5. Czy zawiera bombę?

contain_bomb(board, position) :- interesting(board, position) and (for each neighbour not_flagged_neighbour(board, neighbour)).

Bomba jest w danym miejscu wtedy gdy pole jest interesujące oraz gdy dowolny sąsiad spełnia predykat not_flagged_neighbours_contain_bombs(board, position).


### Szczegóły

Oczywiście predykaty mogą być wykonywane jednokrotnie i ich wyniki zapamiętywane w celach optymalizacyjnych.

### Komentarze

W przypadku gdy któryś z tych predykatów był złym pomysłem, bądź w przypadku lepszych proszę o edycję tego pliku w celu ich dodania.
