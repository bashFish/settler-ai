import time
from map import initialize_map
from misc import *
from events import UiEvent, GameEvent

gameconf = parse_gameconf()
buildings, _ = parse_buildings()


# fetches events of both ui and state,
#   processes and forwards them to the other component
class Game:
    def __init__(self, state):
        self.state = state

    def game_event_update(self):
        for (e, d) in self.state.fetch_reset_game_events():
            if e == GameEvent.ADD_BUILDING:
                cell, building = d
                print("Building: %s" % (repr(d)))
                self.state.add_ui_event(UiEvent.ADD_BUILDING, (cell, buildings[building]['key']))

    def update(self):
        self.state.increment_tick()
        self.game_event_update()

    def mainloop(self):

        #TODO: geht das wirklich nicht besser? kommt mir sehr ineffizient vor,
        # wenn die prozesse so mühseelig nen state updaten müssen :/
        ls_occ, ls_ra, main_building_position = initialize_map(self.state.get_landscape_occupation(), self.state.get_landscape_resource_amount())
        self.state.set_landscape_occupation_complete(ls_occ)
        self.state.set_landscape_resource_amount_complete(ls_ra)
        self.state.force_add_building(main_building_position, "Base")
        self.state.add_ui_event(UiEvent.INIT)

        while True:
            start = time.time()
            self.update()
            sleep = gameconf['tick_rate'] - (time.time() - start)

            if sleep > 0.:
                time.sleep(sleep)
