# Part one

# We have a system of hexagonal tiles, all starting face up (white), with a black reverse side, and a central tile at (0,0). The task is to follow each set of instructions (east, south east, west etc) and flip the tile that you land on. Then at the end, count the number of black tiles. Remember, one tile can be flipped several times.

# convert instructions to cartesian coords
def comp_to_coords(comp_direct):
    """
    Convert compass directions to cartesion coords (imagined for hexagonal tiles)
    """
    if comp_direct == 'e':
        x, y = 2, 0
    elif comp_direct == 'se':
        x, y = 1, -1
    elif comp_direct == 'sw':
        x, y = -1, -1
    elif comp_direct == 'w':
        x, y = -2, 0
    elif comp_direct == 'nw':
        x, y = -1, 1
    elif comp_direct == 'ne':
        x, y = 1, 1

    return x, y


# use a context manager to read lines from text file
with open('day24_input.txt', 'r') as f:
    file_contents = f.read()

# split by new line and remove any empty strings
directions = file_contents.split('\n')
directions = [direct for direct in directions if direct.split()]

# iterate through the list and split each string into a list of instructions
directs_l = []
for direct in directions:

    direct_sep = direct.replace('e', 'e,')
    direct_sep = direct_sep.replace('w', 'w,')
    direct_sep = direct_sep.rstrip(',').split(',')

    directs_l.append(direct_sep)

# for each set of instructions, loop through the instructions, follow the coordinates (i.e. x+=this_x etc),
# and if this coordinate is not a key in the dict, store it as a black tile (-1). If it is in the dict, flip it (*-1).
# white = 1, black = -1, all start as white:
tiles_dict = {}
for tile_direct in directs_l:
    x = 0
    y = 0
    for comp_direct in tile_direct:  # read the compass instructions and follow in cartesian coords
        this_x, this_y = comp_to_coords(comp_direct)
        x += this_x
        y += this_y

    if (x, y) not in tiles_dict:  # if land on new tile, create and make black -> -1
        tiles_dict[x, y] = -1
    else:  # flip
        tiles_dict[x, y] = tiles_dict[x, y] * -1

# count and print the number of black tiles
black_tile_count = 0
for tile in tiles_dict.values():
    if tile == -1:
        black_tile_count += 1

print(f'There are {black_tile_count} black tiles')


# Part two is a game of life style simulation

# The two rules are:
# 1. black tile and either 0 or >2 neighbouring black tiles -> white
# 2. white tile and 2 neighbouring black tiles -> black

# The task is to run the simulation x100 and return the total number of black tiles.

def make_list_neighbours(x, y):
    """
    accepts cartesian coords and returns a list of tuples of all the hexagonal neighbours
    """
    return [(x + 2, y), (x + 1, y - 1), (x - 1, y - 1), (x - 2, y), (x - 1, y + 1), (x + 1, y + 1)]


def create_dict_neighbs(tiles_dict):
    """
    create dictionary of tiles with all the neighbours. If a tile not previously present, make white (1)
    """
    tiles_dict_new = tiles_dict.copy()
    for tile_xy, tile_col in tiles_dict.items():
        # create all poss neighbours
        neighbs_l = make_list_neighbours(tile_xy[0], tile_xy[1])
        for neighb in neighbs_l:  # iterate through poss neighbs
            if neighb not in tiles_dict:  # if tile not in dict, create and make white
                tiles_dict_new[neighb[0], neighb[1]] = 1

    return tiles_dict_new


def flip_tiles_simultaneously(tiles_dict):
    """
    create new dict with neighbours, check all tiles for neighbs, create new dict with flipped tiles
    (then final step is to put into loop)
    """
    tiles_dict_flipped = tiles_dict.copy()
    for tile_xy, tile_col in tiles_dict.items():
        numb_blacks = 0
        # create all poss neighbours and count blacks
        neighbs_l = make_list_neighbours(tile_xy[0], tile_xy[1])
        for neighb in neighbs_l:
            if (neighb in tiles_dict) and (tiles_dict[neighb[0], neighb[1]] == -1):
                numb_blacks += 1

        # know numb of black neighbours, so apply rules
        # black and either 0 or >2 black neighbs -> white
        if ((tile_col == -1) and (numb_blacks == 0)) or ((tile_col == -1) and (numb_blacks > 2)):
            tiles_dict_flipped[tile_xy[0], tile_xy[1]] = 1
        elif (tile_col == 1) and (numb_blacks == 2):  # white and 2 black neighbs -> black
            tiles_dict_flipped[tile_xy[0], tile_xy[1]] = -1
        else:
            continue

    return tiles_dict_flipped


def number_black_tiles(tiles_dict):
    """
    return number of black tiles (-1) in dict
    """
    black_tile_count = 0
    for tile in tiles_dict.values():
        if tile == -1:
            black_tile_count += 1

    return black_tile_count


# now run the simulation x100 (store results in a list in case want to plot)
numb_black_list = []
for i in range(100):

    # make dict with neighbours
    tiles_dict = create_dict_neighbs(tiles_dict)

    #  flip the tiles
    tiles_dict = flip_tiles_simultaneously(tiles_dict)

    # count the number blacks
    numb_blacks = number_black_tiles(tiles_dict)

    # store in list in case wish to visualise simulation later
    numb_black_list.append(numb_blacks)

print(f'There are {numb_black_list[-1]} black tiles')
