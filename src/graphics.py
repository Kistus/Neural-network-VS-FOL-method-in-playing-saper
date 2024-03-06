import time
import tkinter
import random
import tkinter.messagebox
import tkinter.simpledialog
import symbols

colors = ['#FFFFFF', '#0000FF', '#008200', '#FF0000',
          '#000084', '#840000', '#008284', '#840084', '#000000']


class Graphics:

    def __init__(self, window, i):
        self.gameover = False
        self.window = window
        self.window.title(str(i))
        self.buttons = []
        self.field = []
        self.size = 9
        self.mines = 9

    def createMenu(self):
        menubar = tkinter.Menu(self.window)
        menusize = tkinter.Menu(self.window, tearoff=0)
        menusize.add_separator()
        self.window.config(menu=menubar)

    def prepareWindow(self):
        self.buttons = []
        for x in range(0, self.size):
            self.buttons.append([])
            for y in range(0, self.size):
                b = tkinter.Button(self.window, text=" ", width=2)
                b.grid(row=x+1, column=y, sticky=tkinter.N +
                       tkinter.W+tkinter.S+tkinter.E)
                self.buttons[x].append(b)
        self.window.update()

    def prepareGame(self, field):
        self.field = field

    def restartGame(self):
        self.gameover = False
        # destroy all - prevent memory leak
        # for x in self.window.winfo_children():
        #     if type(x) != tkinter.Menu:
        #         x.destroy()

    def clickOn(self, x, y):
        global colors

        if self.gameover:
            return
        self.buttons[x][y]["text"] = str(self.field[x, y])
        if self.field[x, y] == symbols.MINE_SYMBOL:
            self.buttons[x][y]["text"] = "*"
            self.buttons[x][y].config(
                background='red', disabledforeground='black')
            self.gameover = True
            for _x in range(0, self.size):
                for _y in range(self.size):
                    if self.field[_x, _y] == symbols.MINE_SYMBOL:
                        self.buttons[_x][_y]["text"] = "*"
        else:
            if self.field[x, y] != symbols.EMPTY_SYMBOL:
                self.buttons[x][y].config(
                    disabledforeground=colors[int(self.field[x, y])])
        if self.field[x, y] == symbols.EMPTY_SYMBOL:
            self.buttons[x][y]["text"] = " "
            # now repeat for all buttons nearby which are 0... kek
            self.autoClickOn(x, y)
        self.buttons[x][y]['state'] = 'disabled'
        self.buttons[x][y].config(relief=tkinter.SUNKEN)
        self.window.update()
        if (self.checkWin() or self.gameover):
            time.sleep(0.5)
            self.restartGame()
            return

    def autoClickOn(self, x, y):
        global colors
        if self.buttons[x][y]["state"] == "disabled":
            return
        if self.field[x, y] != symbols.EMPTY_SYMBOL and self.field[x, y] != symbols.MINE_SYMBOL:
            self.buttons[x][y]["text"] = str(self.field[x, y])
            self.buttons[x][y].config(
                disabledforeground=colors[int(self.field[x, y])])
        else:
            self.buttons[x][y]["text"] = " "
        self.buttons[x][y].config(relief=tkinter.SUNKEN)
        self.buttons[x][y]['state'] = 'disabled'
        if self.field[x, y] == symbols.EMPTY_SYMBOL:
            if x != 0 and y != 0:
                self.autoClickOn(x-1, y-1)
            if x != 0:
                self.autoClickOn(x-1, y)
            if x != 0 and y != self.size-1:
                self.autoClickOn(x-1, y+1)
            if y != 0:
                self.autoClickOn(x, y-1)
            if y != self.size-1:
                self.autoClickOn(x, y+1)
            if x != self.size-1 and y != 0:
                self.autoClickOn(x+1, y-1)
            if x != self.size-1:
                self.autoClickOn(x+1, y)
            if x != self.size-1 and y != self.size-1:
                self.autoClickOn(x+1, y+1)
        self.window.update()

    def onRightClick(self, x, y):
        if self.gameover:
            return
        if self.buttons[x][y]["text"] == "?":
            self.buttons[x][y]["text"] = " "
            self.buttons[x][y]["state"] = "normal"
        elif self.buttons[x][y]["text"] == " " and self.buttons[x][y]["state"] == "normal":
            self.buttons[x][y]["text"] = "?"
            self.buttons[x][y]["state"] = "disabled"

    def checkWin(self):
        win = True
        for x in range(0, self.size):
            for y in range(0, self.size):
                if self.field[x, y] != symbols.MINE_SYMBOL and self.buttons[x][y]["state"] == "normal":
                    win = False
        return win
