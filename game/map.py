import random

rows = 50
cols = 50


# TODO: should be moved into environment!
def initialize_map(landscape_occupation, landscape_resource_amount):

    # place wood
    for i in range(6):
        cell = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        for j in range(10):
            x_d = random.randint(0, 2) - 1
            y_d = random.randint(0, 2) - 1
            cell = tuple(map(sum, zip(cell, (x_d, y_d))))
            if cell[0] < 0 or cell[1] < 0 or cell[0] >= cols or cell[1] >= rows:
                continue

            #TODO: needs to call a function rather
            landscape_occupation[cell[0], cell[1]] = 8
            landscape_resource_amount[cell[0], cell[1]] = 9

    # make space for main building
    middle = (int(rows / 2), int(cols / 2))

    # TODO: needs to call a function rather
    landscape_occupation[(middle[0] - 5):(middle[0] + 5), (middle[1] - 5):(middle[1] + 5)] = 0
    landscape_resource_amount[(middle[0] - 5):(middle[0] + 5), (middle[1] - 5):(middle[1] + 5)] = 0

    return landscape_occupation, landscape_resource_amount, middle