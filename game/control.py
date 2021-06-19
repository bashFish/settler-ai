import time
from map import initialize_map
from misc import *
from events import UiEvent, GameEvent

gameconf = parse_gameconf()
buildings, _, _ = parse_buildings()

# fetches events of both ui and environment,
#   processes and forwards them to the other component
class Control:
    def __init__(self, environment, ls_ra = None, ls_occ = None, building = None):
        self.environment = environment
        self._RUNNING = True
        self.ls_ra = ls_ra
        self.ls_occ = ls_occ
        self.building = building

    def game_event_update(self):
        for (e, d) in self.environment.fetch_reset_game_events():
            if e == GameEvent.DROP:
                self.environment.delete_at(d)
            if e == GameEvent.END_GAME:
                self._RUNNING = False
                self.environment.add_ui_event(UiEvent.DRAW_DASHBOARD)
            if e == GameEvent.CONSTRUCT_BUILDING:
                #TODO: should be called each tick with do_construct()
                cell, building = d
                #print("Building: %s" % (repr(d)))
                result = self.environment.construct_building(cell, building)
                if result:
                    self.environment.add_ui_event(UiEvent.ADD_BUILDING, (cell, "Construction"))
            if e == GameEvent._ADD_BUILDING:
                #TODO: should be called each tick with tick()
                cell, building = d
                print("Building added: %s %s" % (repr(d), self.environment.tick))
                result = self.environment.do_add_building(cell, building)
                if result:
                    self.environment.add_ui_event(UiEvent.ADD_BUILDING, (cell, building))
                if result == 'extend':
                    self.environment.add_ui_event(UiEvent.DRAW_TERRAIN)

    def update(self):
        self.environment.increment_tick()
        self.game_event_update()

    def initialize_state(self):
        #TODO: geht das wirklich nicht besser? kommt mir sehr ineffizient vor,
        # wenn die prozesse so mühseelig nen environment updaten müssen :/
        if self.ls_ra is not None and self.ls_occ is not None and self.building is not None:
            ls_occ = self.ls_occ
            ls_ra = self.ls_ra
            main_building_position = self.building
        else:
            ls_occ, ls_ra, main_building_position = initialize_map(self.environment.get_landscape_occupation(), self.environment.get_landscape_resource_amount())
        self.environment.set_landscape_occupation_complete(ls_occ)
        self.environment.set_landscape_resource_amount_complete(ls_ra)
        self.environment.do_add_building(main_building_position, "Base")
        self.environment.add_ui_event(UiEvent.INIT)

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