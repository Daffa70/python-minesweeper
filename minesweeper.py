# Python Version 2.7.3
# File: minesweeper.py

from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
import time
from datetime import time, date, datetime
import shelve

SIZE_X = 10
SIZE_Y = 10
TIMER_GAME_OVER = "00:00:05"

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"


window = None
window = Tk()
# set program title
window.title("Minesweeper")


class Minesweeper:

    def __init__(self, tk, x, y, time):
        global SIZE_X
        global SIZE_Y
        global TIMER_GAME_OVER

        SIZE_X = x
        SIZE_Y = y
        TIMER_GAME_OVER = time
        self.SCORE = 0

        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "clicked": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(
                PhotoImage(file="images/tile_"+str(i)+".gif"))

        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()
        self.tk.geometry("600x600")

        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "mines": Label(self.frame, text="Mines: 0"),
            "flags": Label(self.frame, text="Flags: 0")
        }
        self.labels["time"].grid(
            row=0, column=0, columnspan=SIZE_Y)  # top full width
        self.labels["mines"].grid(
            row=SIZE_X+1, column=0, columnspan=int(SIZE_Y/2))  # bottom left
        self.labels["flags"].grid(
            row=SIZE_X+1, column=int(SIZE_Y/2)-1, columnspan=int(SIZE_Y/2))  # bottom right
        Button(self.tk, text="Reset Game",
               font=10, fg="red",
               bg="black", command=self.restartGame).pack(pady=20)

        self.restart()
        self.updateTimer()

    def restartGame(self):
        self.restart()

    def setup(self):

        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0
        self.startTime = None

        self.tiles = dict({})
        self.mines = 0
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + "_" + str(y)
                isMine = False

                gfx = self.images["plain"]

                if random.uniform(0.0, 1.0) < 0.1:
                    isMine = True
                    self.mines += 1

                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(self.frame, image=gfx),
                    "mines": 0
                }

                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))

                tile["button"].grid(row=x+1, column=y)

                self.tiles[x][y] = tile

        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc

    def restart(self):
        self.setup()
        self.refreshLabels()

    def refreshLabels(self):
        self.labels["flags"].config(text="Flags: "+str(self.flagCount))
        self.labels["mines"].config(text="Mines: "+str(self.mines))

    def gameOver(self, won):
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(
                        image=self.images["wrong"])
                if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(
                        image=self.images["mine"])

        self.tk.update()

        d = shelve.open('score.txt')  # here you will save the score variable
        # thats all, now it is saved on disk.
        d['score'] = self.SCORE
        d.close()
        msg = "Menang! Main Lagi?" if won else "Kalah! Main lagi?"
        res = tkMessageBox.askyesno("Game Over", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()

    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0]
            if delta.total_seconds() < 36000:
                ts = "0" + ts

        if ts == TIMER_GAME_OVER:
            self.gameOver(False)
        self.labels["time"].config(text=ts)
        self.frame.after(100, self.updateTimer)

    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x-1,  "y": y-1},  # top right
            {"x": x-1,  "y": y},  # top middle
            {"x": x-1,  "y": y+1},  # top left
            {"x": x,    "y": y-1},  # left
            {"x": x,    "y": y+1},  # right
            {"x": x+1,  "y": y-1},  # bottom right
            {"x": x+1,  "y": y},  # bottom middle
            {"x": x+1,  "y": y+1},  # bottom left
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile["isMine"] == True:

            self.gameOver(False)
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            self.clearSurroundingTiles(tile["id"])
            self.SCORE += 1
        else:
            tile["button"].config(
                image=self.images["numbers"][tile["mines"]-1])

        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (SIZE_X * SIZE_Y) - self.mines:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image=self.images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)

            if tile["isMine"] == True:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()

        elif tile["state"] == 2:
            tile["button"].config(image=self.images["plain"])
            tile["state"] = 0
            tile["button"].bind(BTN_CLICK, self.onClickWrapper(
                tile["coords"]["x"], tile["coords"]["y"]))

            if tile["isMine"] == True:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()

    def clearSurroundingTiles(self, id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.images["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(
                image=self.images["numbers"][tile["mines"]-1])

        tile["state"] = STATE_CLICKED
        self.clickedCount += 1


def openNewWindowEasy():
    window.destroy()
    newWindow = Tk()

    newWindow.title("Minesweeper Mudah")

    newWindow.geometry("400x400")

    minesweeper = Minesweeper(newWindow, 6, 6, "00:00:03")


def openNewWindowMed():
    window.destroy()
    newWindow = Tk()

    newWindow.title("Minesweeper Sedang")

    newWindow.geometry("400x400")

    minesweeper = Minesweeper(newWindow, 15, 15, "00:04:00")


def openNewWindowHigh():
    window.destroy()
    newWindow = Tk()

    newWindow.title("Minesweeper Susah")

    newWindow.geometry("400x400")

    minesweeper = Minesweeper(newWindow, 20, 20, "00:05:00")
    newWindow.mainloop()


def main():
    window.geometry("300x300")
    Label(window,
          text="Minesweeper",
          font="normal 20 bold",
          fg="blue").pack(pady=20)

    frame = Frame(window)
    frame.pack()

    d = shelve.open('score.txt')
    score = "High Score = " + str(d['score'])  # the score is read from disk
    d.close()
    Label(window,
          text=score,
          font="normal 20 bold",
          fg="blue").pack(pady=5)

    frame = Frame(window)
    frame.pack()

    l4 = Label(window,
               text="Level",
               font="normal 20 bold",
               bg="white",
               width=15,
               borderwidth=2,
               relief="solid")
    l4.pack(pady=20)

    frame1 = Frame(window)
    frame1.pack()

    b1 = Button(frame1, text="Mudah",
                font=10, width=7,
                command=openNewWindowEasy)

    b2 = Button(frame1, text="Sedang",
                font=10, width=7,
                command=openNewWindowMed)

    b3 = Button(frame1, text="Susah",
                font=10, width=7,
                command=openNewWindowHigh)

    b1.pack(side=LEFT, padx=10)
    b2.pack(side=LEFT, padx=10)
    b3.pack(padx=10)

    window.mainloop()


if __name__ == "__main__":
    main()
