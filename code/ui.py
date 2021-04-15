from tkinter import *
import time
import numpy as np
from enum import Enum, auto


size_of_board = 600
rows = 50
cols = 50
DELAY = 500

row_h = int(size_of_board / rows)
col_w = int(size_of_board / cols)

RED_COLOR = "#EE4035"
BLUE_COLOR = "#0492CF"
ORANGE_COLOR = "#FFB233"
GREEN_COLOR = "#7BC043"

BLUE_COLOR_LIGHT = '#67B0CF'
RED_COLOR_LIGHT = '#EE7E77'


class UIState(Enum):
    Running = 1
    DrawGameOver = 2
    Waiting = 3

class CellState(Enum):
    Empty = auto()
    Mountain = auto()
    Water = auto()
    Wood = auto()
    Stone = auto()
    Building = auto()

class ColorMap(Enum):
    Mountain = ORANGE_COLOR
    Water = BLUE_COLOR
    Wood = GREEN_COLOR
    Building = RED_COLOR

class KeyboardMap(Enum):
    Start = 's'
    Building = 'b'
    Wood = 't'
    Water = 'w'
    Mountain = 'm'
    #Field ...

class BuildingMap(Enum):
    Base = auto()
    Well = auto()
    Stone = auto()
    Forester = auto()
    Woodcutter = auto()
    Sawmill = auto()
    Hunter = auto()
    Fishery = auto()
    Farm = auto()
    Mill = auto()
    Baker = auto()
    Barack = auto()
    #CoalMine = auto()
    #IronMine = auto()
    #GoldMine = auto()
    #Smith = auto()
    #ToolMaker = auto()
    #CoinMaker = auto()

# Goal: for now: get as fast as possible 10, 100, 1000 bread. or: get as much bread as possible, in 10, 100, 1000 game ticks.
# ressources: 1 ressource distributed per game tick. wood requires 4 game ticks, stone 7 ticks
#
#    bread requires: food, flour, water.
#     food -> fisher/ hunter
#     flour -> mill -> corn
#     corn -> farm
#     water -> well
#
#  well:
class SettlerUi:

    # ------------------------------------------------------------------
    # Initializing Functions/ Loops:
    # ------------------------------------------------------------------
    def __init__(self, gamestate):

        self._gamestate = gamestate

        self.window = Tk()
        self.window.title("Settler-UI")

        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board+20)
        self.canvas.pack()

        self.window.bind("<Key>", self.key_input)
        self.window.bind("<Button-1>", self.mouse_input)

        self.reset()

    def draw_raster(self):
        for i in range(rows):
            self.canvas.create_line(
                i * size_of_board / rows, 0, i * size_of_board / rows, size_of_board, fill='lightgray'
            )

        for i in range(cols):
            self.canvas.create_line(
                0, i * size_of_board / cols, size_of_board, i * size_of_board / cols, fill='lightgray'
            )

    def reset(self):
        self._board = []
        self._objects = []
        self._new_objects = []
        self._last_key_pressed = None
        self._begin_time = None
        self._state = None
        self._begin_time = time.time()
        self._state = UIState.Waiting
        self._stats_canvas = None

        self.canvas.delete("all")
        self.draw_raster()

    def mainloop(self):
        while True:
            self.window.update()
            self.update()
            print("state %s" % (self._state))

            if self._state == UIState.Running:
                time.sleep(.5)
            elif self._state == UIState.DrawGameOver:
                self.display_gameover()
                self._state = UIState.Waiting
            elif self._state == UIState.Waiting:
                time.sleep(1)

    # ------------------------------------------------------------------
    # Drawing Functions:
    # ------------------------------------------------------------------
    def display_gameover(self):
        score = 10
        self.canvas.delete("all")
        score_text = "you scored \n"
        self.canvas.create_text(
            size_of_board / 2,
            3 * size_of_board / 8,
            font="cmr 40 bold",
            fill=GREEN_COLOR,
            text=score_text,
        )
        score_text = str(score)
        self.canvas.create_text(
            size_of_board / 2,
            1 * size_of_board / 2,
            font="cmr 50 bold",
            fill=BLUE_COLOR,
            text=score_text,
        )
        time_spent = str(np.round(time.time() - self._begin_time, 1)) + ' sec'
        self.canvas.create_text(
            size_of_board / 2,
            3 * size_of_board / 4,
            font="cmr 20 bold",
            fill=BLUE_COLOR,
            text=time_spent,
        )
        score_text = "click to play again \n"
        self.canvas.create_text(
            size_of_board / 2,
            15 * size_of_board / 16,
            font="cmr 20 bold",
            fill="gray",
            text=score_text,
        )

    # ------------------------------------------------------------------
    # Logic Functions:
    # ------------------------------------------------------------------
    @staticmethod
    def _cell_to_coordinates(cell):
        x1 = cell[0] * row_h
        y1 = cell[1] * col_w
        x2 = x1 + row_h
        y2 = y1 + col_w
        return [x1, y1, x2, y2]

    @staticmethod
    def _coordinates_to_cell(coords):
        x = int(coords[0] / row_h)
        y = int(coords[1] / col_w)

        if x < 0 or y < 0:
            return None
        if x >= cols or y >= rows:
            return None

        return [x, y]

    def update(self):
        if self._last_key_pressed == KeyboardMap.Start:
            self._state = UIState.Running
            self._last_key_pressed = None

        if self._new_objects:
            for o in self._new_objects:
                oc = self.canvas.create_rectangle(
                    self._cell_to_coordinates(o[0]), fill=Color, outline='gray',
                )
                self._objects.append(o + (oc, ))
            self._new_objects = []

        stats_text = "you scored \n"
        self._stats_canvas = self.canvas.create_text(
            size_of_board/2,
            size_of_board + 25,
            font="cmr 15 bold",
            fill='black',
            text=stats_text,
        )

    def mouse_input(self, event):
        print("Mouse: %s" %(event))
        cell = self._coordinates_to_cell([event.x, event.y])
        if cell:
            self._new_objects.append((cell,self._last_key_pressed))

    def key_input(self, event):
        print("Keyboard: %s" %(event))
        if event.keysym in KeyboardMap._value2member_map_:
            self._last_key_pressed = KeyboardMap._value2member_map_[event.keysym]
