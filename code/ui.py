from tkinter import *
import time
import numpy as np
from enum import Enum, auto
import json

from events import UiEvent

with open('config/game.json') as fp:
    gameconf = json.load(fp)

with open('config/colors.json') as fp:
    colors = json.load(fp)

size_of_board = 500
rows = 50
cols = 50
DELAY = 500

row_h = int(size_of_board / rows)
col_w = int(size_of_board / cols)
row_h_2 = row_h/2
col_w_2 = col_w/2


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
    # Field ...


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
    # CoalMine = auto()
    # IronMine = auto()
    # GoldMine = auto()
    # Smith = auto()
    # ToolMaker = auto()
    # CoinMaker = auto()


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



class Ui:

    # ------------------------------------------------------------------
    # Initializing Functions/ Loops:
    # ------------------------------------------------------------------
    # TODO: in java would only get a very shallow view-interface!
    #     but there are too many object informations that would need inference
    def __init__(self, gamestate):

        self._gamestate = gamestate

        self.window = Tk()
        self.window.title("Settler-UI")

        self.canvas = Canvas(self.window, width=size_of_board+200, height=size_of_board)
        self.canvas.pack()

        self.window.bind("<Key>", self.key_input)
        self.window.bind("<Button-1>", self.mouse_input)

        self.reset()
        self.enqueue_entire_gamestate()

    def draw_raster(self):
        for i in range(rows):
            self.canvas.create_line(
                i * size_of_board / rows, 0, i * size_of_board / rows, size_of_board, fill='lightgray'
            )

        for i in range(cols):
            self.canvas.create_line(
                0, i * size_of_board / cols, size_of_board, i * size_of_board / cols, fill='lightgray'
            )

    def enqueue_entire_gamestate(self):
        ls_occ = self._gamestate.get_landscape_occupation()
        occupied = np.where(ls_occ > 0)
        for x,y in zip(occupied[0], occupied[1]):
            self.register_new_object((x, y), str(ls_occ[x, y]))

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
        self._ticks_canvas = None

        self.canvas.delete("all")
        self.draw_raster()


    def game_event_update(self):
        for e in self._gamestate.fetch_reset_ui_events():
            pass
            #if e == UiEvent.UpdateTick:  #TODO: maybe this one can be default :S? but nice it works :D
            #    self.update_ticks_text()

    def ui_event_update(self):
        if self._last_key_pressed == KeyboardMap.Start:
            self._state = UIState.Running
            self._last_key_pressed = None

        if self._new_objects:
            for o in self._new_objects:
                oc = self.mark_cell(o[0], o[1])
                self._objects.append(o + (oc,))
            self._new_objects = []


    def update(self):
        self.window.update()

        self.update_ticks_text()
        self.update_gamestats_text() #TODO: this one only at event?

        self.game_event_update()
        self.ui_event_update()

        # TODO: do i need these states?
        if self._state == UIState.Running:
            pass
        elif self._state == UIState.DrawGameOver:
            self.display_gameover()
            self._state = UIState.Waiting
        elif self._state == UIState.Waiting:
            pass

    def mainloop(self):
        while True:
            start = time.time()
            self.update()
            sleep = gameconf['frame_rate'] - (time.time() - start)

            if sleep > 0.:
                time.sleep(sleep)

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

    def mark_cell(self, cell, object):
        coords = self._cell_to_coordinates(cell)
        color = 'gray' # object to color
        symbol = object #'h'

        cvs = []
        cvs.append(self.canvas.create_rectangle(
            coords, fill=color, outline='gray',
        ))
        cvs.append(self.canvas.create_text(
            coords[0] + col_w_2,
            coords[1] + row_h_2,
            font="cmr 9 bold",
            fill='black',
            text=symbol,
        ))
        return cvs

    def key_to_object(self, key):
        return key


    def update_gamestats_text(self):
        if self._stats_canvas:
            self.canvas.delete(self._stats_canvas)

        state_dict = self._gamestate.get_state_dict()
        #TODO: should rather be accessed thru keys
        gamestats = "settler: %i  wood: %i  plank: %i" % (state_dict['settler'], state_dict['wood'], state_dict['plank'])

        self._stats_canvas = self.canvas.create_text(
            size_of_board + 2,
            10,
            font="times 11 bold",
            fill='black',
            text=gamestats,
            anchor=W
        )

    def update_ticks_text(self):
        if self._ticks_canvas:
            self.canvas.delete(self._ticks_canvas)

        tick = "tick: %i/ %i" % (self._gamestate.get_ticks())

        self._ticks_canvas = self.canvas.create_text(
            size_of_board + 2,
            50,
            font="times 11 bold",
            fill='black',
            text=tick,
            anchor=W
        )

    def register_new_object(self, cell, object):
        self._new_objects.append((cell,  object))

    def mouse_input(self, event):
        print("Mouse: %s" % (event))
        cell = self._coordinates_to_cell([event.x, event.y])
        if cell:
            self.register_new_object(cell,  self.key_to_object(self._last_key_pressed))

    def key_input(self, event):
        print("Keyboard: %s" % (event))
        if event.keysym in KeyboardMap._value2member_map_:
            self._last_key_pressed = KeyboardMap._value2member_map_[event.keysym]
