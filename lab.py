# 6.009 Lab 2: Snekoban

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def getdirec(direc):
    '''Return Direction vector given direction'''
    if direc=='up':
        return [-1,0]
    elif direc=='down':
        return [1,0]
    elif direc=='left':
        return [0,-1]
    elif direc=='right':
        return [0,1]



def new_game(level_description):
    """
    Given a description of a game state, return dictionary of coordinates of important components

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    A dictionary will be returned with keys for computers, player, walls, and targets, with corresponding sets containing coordinates of these components
    
    """

    height = len(level_description)
    width = len(level_description[0])
    newgame = {'computers': set(), 'walls': set(), 'player': set(), 'targets': set(),'height':height,'width':width} #initializes the dictionary
    for i in range(height):
        for j in range(width): #go through each point in game and add coordinates to whatever object(s) is/are in that space
            if (len(level_description[i][j]) == 2): # checks if two objects in 1 spot
                newgame['targets'].add((i,j))
                if(level_description[i][j][1]=='player'): # check if player in 2nd spot
                    newgame['player'].add((i,j))
                else:
                    newgame['computers'].add((i,j)) #else, must be computer
            elif (len(level_description[i][j]) == 0): # Could be empty spot
                continue
            else:
                if (level_description[i][j][0] == 'wall'): # check if spot is wall
                    newgame['walls'].add((i,j))
                elif (level_description[i][j][0] == 'player'): #check if spot is player
                    newgame['player'].add((i,j))
                elif (level_description[i][j][0] == 'computer'): #check if computer
                    newgame['computers'].add((i,j))
                elif (level_description[i][j][0] == 'target'): #check if target
                    newgame['targets'].add((i,j))
    return newgame


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    if(len(game['computers'])!=0): #if 0 computers, game is false
        if(game['computers']==game['targets']): # The coordinates of computers and targets must all be the same, no extras allowed
            return True
    return False




def step_game(game, direction):
    '''Given game and direction, returns updated board with move made in that direction'''
    newgame = {'computers': game['computers'].copy(), 'walls': game['walls'].copy(), 'player': game['player'].copy(), 'targets': game['targets'].copy(), 'height': game['height'], 'width': game['width']}
    for e in game['player']:
        playerpos=e

    playh=playerpos[0] # Take coordinates of player
    playw=playerpos[1]
    x=getdirec(direction)[0] #Takes direction coordinates
    y=getdirec(direction)[1]
    if (x + playh < 0 or x + playh > (game['height'] - 1)): # checks if move is in game board
        return newgame
    if (y + playw < 0 or y + playw > (game['width'] - 1)):
        return newgame
    if((playh+x,playw+y) in game['walls']): #stops if wall in next space
        return newgame
    if ((playh+x,playw+y) not in game['computers']): # moves once if possible (no wall or computer)
        newgame['player'].remove((playh,playw))
        newgame['player'].add((playh+x,playw+y))
        return newgame
    if not (0<= 2*x+playh <=(game['height'] - 1)): #Must be a computer, so see if 2 steps away from player is in board
        return newgame
    if not (0<= 2*y+playw <=(game['width'] - 1)):
        return newgame
    if((playh+2*x,playw+2*y) in game['computers'] or (playh+2*x,playw+2*y) in game['walls']): # Nothing to do if 2 steps away from player is not empty
        return newgame
    newgame['player'].remove((playh, playw)) # Remove player initial coordinates
    newgame['player'].add((playh + x, playw + y)) # Add player new coordinares
    newgame['computers'].remove((playh+x, playw+y)) # Add computer old coordinates
    newgame['computers'].add((playh + 2*x, playw + 2*y)) # Add computer new coordinates
    return newgame
        





def dump_game(game):
    """
    Given a dictionary of component coordinates, convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    
    """
    newgame=[]
    for i in range(game['height']):
        newgame.append([])
        for j in range(game['width']):
            newgame[i].append([])
    for e in game['walls']:
        newgame[e[0]][e[1]].append('wall')
    for e in game['targets']:
        newgame[e[0]][e[1]].append('target')
    for e in game['computers']:
        newgame[e[0]][e[1]].append('computer')
    for e in game['player']:
        newgame[e[0]][e[1]].append('player')
    return newgame


def solve_puzzle(game):
    """
    Given dictionary of game components and coordinates, find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    targets = game['targets']
    walls = game['walls']
    height = game['height']
    width = game['width']
    computers = game['computers'].copy() # Makes copy of computer set
    player = game['player'].copy() # Makes copy of player coordinate set
    d={'player':player,'computers':computers,'moves':[]} # creates dictionary with players, computers, and moves, Everything that can change
    positions=[d] # our queue of dictionaries of positions and moves
    visited=set() #Lets us see positions we have already been to
    a=1
    new=d
    while(a!=0): # While no solution found
        if(len(positions)==0): #If no more configurations to consider, no solutions possible
            return None
        new=positions.pop(0) #pop oldest element of queue to check as it is closest to initial position
        newgame={'player':new['player'], 'computers':new['computers'], 'targets':targets,'walls':walls,'height':height,'width':width}
        if (victory_check(newgame) == True): #checks if we are done
            a=0
        else:
            setofdirec=['up','down','left','right']
            for dir in setofdirec: #For every direction, move player once in that direction
                game1=step_game(newgame,dir) #creates new positions
                v=(tuple(game1['player']),tuple(game1['computers'])) # Creates tuple for visited for new position
                if (v not in visited): # Makes sure we are considering a new position
                    visited.add(v)
                    moves=new['moves'][:]
                    moves.append(dir) # Updates move list with new move
                    positions.append({'player':game1['player'],'computers':game1['computers'],'moves':moves}) # If it is a new position, we add it to our queue           
            a=1 # keep loop going
    return new['moves']








    
