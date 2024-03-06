from tkinter import Tk
from graphics import Graphics
from minesweeper import Minesweeper
from board import Board
import minesweeperio
import fol.predicates
import fol.utils
import fol.agent
import fol.interpreter

board = minesweeperio.read_board_from_file("board.example")


def lost_game():
    print('Example game lost by a player')
    game = Minesweeper(board)
    game.print_closed_board()
    game.set_flag(4, 1)
    game.click(6, 1)
    game.click(1, 5)
    game.print_closed_board()
    return game


def won_game():
    print('Example game won by a player')
    game = Minesweeper(board)
    game.print_closed_board()
    game.click(5, 4)
    # Current implementation doesn't require to set every flag, as long as everything other than mines is available
    # game.set_flag(2, 1)
    # game.set_flag(3, 2)
    # game.set_flag(4, 2)
    # game.set_flag(8, 2)
    # game.set_flag(8, 3)
    # game.set_flag(1, 5)
    # game.set_flag(9, 5)
    # game.set_flag(9, 8)
    game.click(9, 9)
    game.click(9, 7)
    game.click(9, 6)
    game.set_flag(3, 7)
    game.set_flag(4, 7)
    game.click(1, 3)
    game.click(1, 1)
    game.click(3, 1)
    game.click(4, 1)
    game.click(8, 1)
    game.click(9, 1)
    game.click(9, 2)
    game.click(9, 3)
    game.click(9, 4)
    game.print_closed_board()
    return game


def show_generated_board():
    b = Board.generate(9, 9)
    print('Example generated board')
    print(b.contents)


def main():
    window = Tk()
    PredicateEvaluator = fol.interpreter.compile_predicates()
    v = PredicateEvaluator(9)
    v.predicate_field_can_be_clicked()
    list_of_neighbour_lists = fol.utils.generate_list_of_neighbour_lists(9)
    list_of_every_positions = fol.utils.generate_every_position_list(9)
    correct = 0
    incorrect = 0
    graf = Graphics(window, 0)

    for i in range(100):

        b = Board.generate(9, 9)

        graf = Graphics(window, i)
        graf.createMenu()
        graf.prepareWindow()
        graf.prepareGame(b.contents)

        g = Minesweeper(b)
        if fol.agent.solver2(g, list_of_neighbour_lists, list_of_every_positions, graf):
            correct += 1
        else:
            incorrect += 1
        graf.restartGame()

    print('correct: ', correct)
    print('incorrect: ', incorrect)
    graf.window.destroy()
    graf.window.mainloop()


if __name__ == '__main__':
    main()
