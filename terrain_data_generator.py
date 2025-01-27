"""
------------------------- Intro ----------------------------

Uses initial seed to generate consistent terrain generation,
loot, and enemy generation is random and only takes place
in empty spaces.

------------------------- Logic ----------------------------

The inital seed is passed through random.seed(), which uses
math to generate a float, converted to an integer, then 
string in ftd().

Each random number generated is consistent 

Rowdata, when called generates one 16 value string, takes the
last value, converts it into an integer, and generates another
16 value string. Both strings are combined and stored as a row

Terrain Generator uses the first two functions to generate
a specified number of rows with 'metadata' that is used to
tell the rest of the program what should appear in game and where.

Each value in the string represents a different in game object,
such as a chunk, open space, an enemy, a reward

This type of generation also allows for custom in game rooms
to be inserted into the world randomly, or via scripted action.

The end goal is to tweak the meanings of values until a balance
is struck between enough navigatable terrain, and expansive caves,
with enough room to fight enemies and to reach the rewards

"""
import random

def ftd():
    """ Generate a random 16 digit string """
    return "{:016d}".format(int(random.random() * (10**16)))


# Call ftd twice to generate 32 digit string
def rowdata(seed):
    random.seed(seed)
    part1 = ftd()
    random.seed(int(part1[-1]))  # Use the last digit of part1 as the new seed
    part2 = ftd()
    return part1 + part2

def terrainmap(init_seed: int, num_rows) -> list:

    col_data = []
    row_last = rowdata(init_seed)
    space = '|' # represents an unbreakable chunk/border
    dirt = 'X'
    gold = '$'
    enemy = '%'
    air = ' '
    

    while len(col_data) < num_rows:
        col_data.append(row_last)
        new_seed = int(row_last) # take seed as int of last_row
        row_last = rowdata(new_seed) # get data of next row with new seed

    for row_index in range(len(col_data)):
        row = col_data[row_index]
        new_row = ""
        for char in row:
            cell = int(char)
            if cell in [2,3,4,5,6]: # block odds
                new_row += dirt
            else:
                 # a bit of unscripted RNG for objects and enemies
                object = random.randrange(25)
                # Rewards
                if object == 1:
                    # Gold won't spawn beside or below other gold
                    if new_row[-1:] and col_data[-1][len(new_row)] != gold: 
                        new_row += gold
                    else: new_row += dirt
                
                elif object == 3 : # 2/30 chance of enemy
                    new_row += enemy
                
                elif object in [5, 6, 7, 8]: # 4/30 chance of unbreakable block
                    new_row += space
                else:
                    new_row += air

        col_data[row_index] = space + new_row + space

    # scripted dividers
    o = space + ' '*32 + space
    x = space + 'X'*32 + space
    logo = space + 'X'*6 + ' '*20 + 'X'*6 + space

    col_data[round(num_rows/2)] = x # middle divider

    col_data.insert(0, x)

    """------------------------ Level Design ------------------------"""
    cavern_ceiling = [
            "|XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX|",
            "|XXX   XXXX   XXXXX  XXX  XXXXXXX|",
            "|X X    XX     XXX   XXX    XXXXX|",
            "|X      X       X      X     XX X|",
            ]

    """----------------------- Spawn Chamber ------------------------"""
    for i in range(4): # open space at spawn level
        col_data.insert(0, logo)

    col_data.insert(0, (space+ 'X'*6 + ' '*18+ '%'+' '+ 'X'*6+space))

    for i in range(4): # open space at spawn level
        col_data.insert(0, logo)
    
    for i in range(3):
        col_data.insert(0, x) # spawn ceiling
    """------------------------ Boss Chamber ------------------------"""

    for i in range(len(cavern_ceiling)):
        col_data.append(cavern_ceiling[i])

    for i in range(9):
        col_data.append(o)
    
    for i in range(12):
        col_data.append('|'*34)

    for i in col_data:
        print(i)

    return col_data
