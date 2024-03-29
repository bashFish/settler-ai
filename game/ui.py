from tkinter import *
import time
import numpy as np
from enum import Enum, auto
from misc import *

import rasterio.features
from events import UiEvent, GameEvent


gameconf = parse_gameconf()
buildings, key_to_building, objectid_to_building = parse_buildings()
colors = parse_colors()


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
    Start = '1'
    DELETE = 'd'
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
    def __init__(self, environment):

        self._environment = environment

        self.window = Tk()
        self.window.title("Settler-UI")

        self.canvas = Canvas(self.window, width=size_of_board+300, height=size_of_board)
        self.canvas.pack()

        self.window.bind("<Key>", self.key_input)
        self.window.bind("<Button-1>", self.mouse_input)

        self.reset()

    def draw_raster(self):
        for i in range(rows):
            self.canvas.create_line(
                i * row_h, 0, i * row_h, size_of_board, fill='lightgray'
            )

        for i in range(cols):
            self.canvas.create_line(
                0, i * col_w, size_of_board, i * col_w, fill='lightgray'
            )

    def refresh_entire_gamestate(self):
        ls_occ = self._environment.get_landscape_occupation()
        occupied = np.where(ls_occ > 0)
        for x, y in zip(occupied[0], occupied[1]):

            self.register_new_object((x, y), ls_occ[x, y])
        self.draw_owned_terrain()

    def draw_owned_terrain(self):
        if self._terrain_canvas:
            self.canvas.delete(self._terrain_canvas)

        owned_terrain = self._environment.get_owned_terrain().astype(np.int16) #TODO: move this conversion somewhere

        result = rasterio.features.shapes(owned_terrain)
        polygon = next(result)
        if polygon[1] == 0.:
            polygon = next(result)

        print(polygon)
        assert polygon[1] == 1.
        assert len(polygon[0]['coordinates']) == 1
        poly_coords = [[(pt[1]*row_h, pt[0]*col_w) for pt in polygon[0]['coordinates'][0]]]

        self._terrain_canvas = self.canvas.create_polygon(poly_coords, fill='', outline='gray', width=2)

    def reset(self):
        self._board = []
        self._objects = []
        self._new_objects = []
        self._last_key_pressed = None
        self._begin_time = None
        self._begin_time = time.time()
        self._stats_canvas = None
        self._ticks_canvas = None
        self._score_canvas = None
        self._terrain_canvas = None
        self._key_canvas = []

        self.canvas.delete("all")
        self.draw_raster()
        self.draw_headlines()
        self.draw_key_binding()

    # ------------------------------------------------------------------
    # Drawing Functions:
    # ------------------------------------------------------------------
    def draw_headlines(self):
        self.canvas.create_text(
            size_of_board,
            140,
            font="times 12 bold",
            fill='black',
            text="keys:",
            anchor=W
        )

    def draw_key_binding(self):
        if self._key_canvas:
            for c in self._key_canvas:
                self.canvas.delete(c)

        self._key_canvas.append(self.canvas.create_text(
            size_of_board,
            160,
            font="times 10 bold",
            fill='black',
            text="Start: 1",
            anchor=W
        ))
        usable_keys = key_to_building.copy()
        usable_keys['d'] = 'Delete'
        usable_keys['q'] = 'Quit' #TODO: populate this once, reuse everywhere

        for i, k in enumerate(usable_keys):
            color = 'black'
            if k == self._last_key_pressed:
                color = 'green'
            self._key_canvas.append(self.canvas.create_text(
                size_of_board,
                175+i*15,
                font="times 10 bold",
                fill=color,
                text="%s: %s" % (usable_keys[k], k),
                anchor=W
            ))

    def display_gameover(self):
        score = self._environment.get_score()
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
        score_text = "restart to play again \n"
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

        return (x, y)

    #TODO: mark_cell should have objectid
    def mark_cell(self, cell, objectid):
        coords = self._cell_to_coordinates(cell)
        color = 'gray' # object to color
        symbol = str(objectid) #'h'
        outline = 'gray'

        if symbol in objectid_to_building:
            symbol = buildings[objectid_to_building[symbol]]['key']
        if symbol == '1':
            symbol = 'b'
        if symbol == '8':
            symbol = 'w'
            color = 'green'
        if symbol == '':
            color = 'white' #TODO: find proper color that is used :/
            outline = 'lightgray'

        cvs = []
        cvs.append(self.canvas.create_rectangle(
            coords, fill=color, outline=outline,
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
        return key_to_building[key]

    def update_gamestats_text(self):
        if self._stats_canvas:
            self.canvas.delete(self._stats_canvas)

        state_dict = self._environment.get_state_dict()
        #TODO: should rather be accessed thru keys
        gamestats = "settler: %i  wood: %i  plank: %i\n carrier: %i/ free: %i" % (state_dict['settler'], state_dict['wood'], state_dict['plank'],
                                                                                state_dict['carrier'], state_dict['freeCarrier'])

        self._stats_canvas = self.canvas.create_text(
            size_of_board + 2,
            20,
            font="times 11 bold",
            fill='black',
            text=gamestats,
            anchor=W
        )

    def update_tick_and_score_text(self):
        if self._ticks_canvas:
            self.canvas.delete(self._ticks_canvas)

        tick = "tick: %i/ %i\nscore: %s" % (*self._environment.get_ticks(), self._environment.get_score())

        self._ticks_canvas = self.canvas.create_text(
            size_of_board + 2,
            70,
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
            print(self._last_key_pressed)
            if self._last_key_pressed == 'd':
                self._environment.add_game_event(GameEvent.DROP, cell)
            else:
                self._environment.add_game_event(GameEvent.CONSTRUCT_BUILDING, (cell, self.key_to_object(self._last_key_pressed)))

    def key_input(self, event):
        print("Keyboard: %s" % (event))
        if event.keysym == 'q':
            self._environment.add_game_event(GameEvent.END_GAME)
        if event.keysym in key_to_building or event.keysym in ['d']:
            self._last_key_pressed = event.keysym #KeyboardMap._value2member_map_[event.keysym]
            self._environment.add_ui_event(UiEvent.DRAW_KEYS)


    def game_event_update(self):
        print("ui event loop")
        for (e,d) in self._environment.fetch_reset_ui_events():
            if e == UiEvent.INIT:           #TODO: directly get/call the function name or sth
                self.refresh_entire_gamestate()
            if e == UiEvent.DRAW_DASHBOARD:
                self.display_gameover()
            if e == UiEvent.DELETE_CELL:
                print("deleting" + str(d))
                self.mark_cell(d,'')
            if e == UiEvent.DRAW_KEYS:
                self.draw_key_binding()
            if e == UiEvent.ADD_BUILDING:
                cell, building = d
                symb = buildings[building]['objectid']
                if 'key' in buildings[building]:
                    symb = buildings[building]['key']
                elif symb == 7:
                    symb = 'c'
                self.register_new_object(cell, symb)
            if e == UiEvent.DRAW_TERRAIN:
                self.draw_owned_terrain()


    def ui_event_update(self):
        if self._new_objects:    #TODO: is this overkill?
            for o in self._new_objects:
                oc = self.mark_cell(o[0], o[1])
                self._objects.append(o + (oc,))
            self._new_objects = []


    def update(self):
        self.window.update()

        self.update_tick_and_score_text()
        self.update_gamestats_text() #TODO: this one only at event?

        self.game_event_update()
        self.ui_event_update()


    def mainloop(self):
        while True:
            start = time.time()
            self.update()
            sleep = gameconf['frame_rate'] - (time.time() - start)

            if sleep > 0.:
                time.sleep(sleep)