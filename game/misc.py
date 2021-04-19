import json


def parse_gameconf():
    #TODO: lookup thru env vars! -> use env or default
    with open('config/game.json') as fp:
        gameconf = json.load(fp)
    return gameconf

#TODO: parse the shit out of it! validate n put it in structures
def parse_buildings():
    #TODO: wird ziemlich oft ausgefueht!
    with open('config/buildings.json') as fp:
        buildings = json.load(fp)

    #key to building:
    key_to_building = {}
    objectid_to_building = {}

    # validate json
    build_keys = []
    for key in buildings:
        cur = buildings[key]
        assert 'settler' in cur

        if 'key' in cur:
            build_keys.append(cur['key'])
            key_to_building[cur['key']] = key
            objectid_to_building[cur['objectid']] = key

    assert len(build_keys) == len(set(build_keys))

    return buildings, key_to_building, objectid_to_building

def parse_colors():
    with open('config/colors.json') as fp:
        colors = json.load(fp)
    return colors