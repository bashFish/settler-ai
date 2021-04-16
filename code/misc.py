import json


def get_gameconf():
    with open('config/game.json') as fp:
        gameconf = json.load(fp)
    return gameconf

def get_buildings():
    with open('config/buildings.json') as fp:
        buildings = json.load(fp)
    return buildings

def get_colors():
    with open('config/colors.json') as fp:
        colors = json.load(fp)
    return colors