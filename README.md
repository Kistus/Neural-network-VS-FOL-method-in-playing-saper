# SI_project

Robimy tu projekt z SI. Przypominam, że wybraliśmy porównanie metody FOL i sieci neuronowej na podstawie gry Minesweeper.
Prosiłbym o dobre podpisanie komitów w języku angielskim, bo można później dodać do CV tą pracę xd
To ma wyglądać typu takiego:

- init: Initialize <nazwa> - jeżeli tworzymy nowy branch czy coś takiego
- feat: <podpisanie> - jeżeli zmieniamy to co było wcześniej napisane
- add: <podpisanie> - jeżeli dodajemy nową funkcjonalność

## Current development stage

1. Game boards can be read/written to a file
2. Player can click on a board in a certain position, flag it or remove the flag that was there before
3. Winning/losing state is checked during every move and handled (by printing appropriate message to stdout)

  
Sieć neuronowa:
  
1 warstwa ukryta (relu)
1 neuron wyjsciowy (sigmoid)
one-hot encoding klas (pole puste, nieistniejące, numer 1, numer 2, ...)
wycinek planszy np. 3x3, ewentualnie zwiększać rozmiar (poza środkowym elementem)

error: mean_squared_error

generowanie danych (plansza, odpowiednie wycinki z użyciem FOL). 
