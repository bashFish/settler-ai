import time
from map import initialize_map
from misc import *
from events import UiEvent, GameEvent

gameconf = parse_gameconf()
buildings, _, _ = parse_buildings()

# fetches events of both ui and state,
#   processes and forwards them to the other component
class Control:
    def __init__(self, state):
        self.state = state
        self._RUNNING = True

    def game_event_update(self):
        for (e, d) in self.state.fetch_reset_game_events():
            if e == GameEvent.DROP:
                self.state.delete_at(d)
            if e == GameEvent.END_GAME:
                self._RUNNING = False
                self.state.add_ui_event(UiEvent.DRAW_DASHBOARD)
            if e == GameEvent.CONSTRUCT_BUILDING:
                #TODO: should be called each tick with do_construct()
                cell, building = d
                print("Building: %s" % (repr(d)))
                result = self.state.construct_building(cell, building)
                if result:
                    self.state.add_ui_event(UiEvent.ADD_BUILDING, (cell, "Construction"))
            if e == GameEvent._ADD_BUILDING:
                #TODO: should be called each tick with tick()
                cell, building = d
                print("Building: %s" % (repr(d)))
                result = self.state.do_add_building(cell, building)
                if result:
                    self.state.add_ui_event(UiEvent.ADD_BUILDING, (cell, building))
                if result == 'extend':
                    self.state.add_ui_event(UiEvent.DRAW_TERRAIN)

    def update(self):
        self.state.increment_tick()
        self.game_event_update()

    def initialize_state(self):
        #TODO: geht das wirklich nicht besser? kommt mir sehr ineffizient vor,
        # wenn die prozesse so mühseelig nen state updaten müssen :/
        ls_occ, ls_ra, main_building_position = initialize_map(self.state.get_landscape_occupation(), self.state.get_landscape_resource_amount())
        self.state.set_landscape_occupation_complete(ls_occ)
        self.state.set_landscape_resource_amount_complete(ls_ra)
        self.state.do_add_building(main_building_position, "Base")
        self.state.add_ui_event(UiEvent.INIT)

    def mainloop(self):
        self.initialize_state()

        while self._RUNNING:
            start = time.time()
            self.update()
            sleep = gameconf['tick_rate'] - (time.time() - start)

            if sleep > 0.:
                time.sleep(sleep)

    def yieldloop(self):
        self.initialize_state()

        while self._RUNNING:
            self.update()
            yield self._RUNNING