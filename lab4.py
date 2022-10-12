#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    bombs: [(0, 0), (1, 0), (1, 1)]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((num_rows,num_cols),bombs)
    

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'bombs': [(0, 0), (1, 0), (1, 1)],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    bombs: [(0, 0), (1, 0), (1, 1)]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'bombs': [(0, 0), (1, 0), (1, 1)],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    bombs: [(0, 0), (1, 0), (1, 1)]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game,(row,col))
    


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    g=render_nd(game,xray)
    return g
    


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    board = render_2d_locations(game,xray)
    output=""
    for i in range(len(board)):
        for j in range(len(board[0])):
            output+=board[i][j]
        if(i!=len(board)-1):
            output+="\n"
    return output



# N-D IMPLEMENTATION

def makearray(dimensions,list,value):
    '''Makes array of given dimensions with all elements equal to value'''
    if len(dimensions)==1:
        for i in range(dimensions[0]):
             list.append(value) # All nested lists made so elements can be added
    else:
        for i in range(dimensions[0]):
            list.append([])
            makearray(dimensions[1:],list[i],value)



  
def getvalue(coord,board):
    '''Returns value at position given by coordimates in array'''
    if(len(coord)==1):
        return board[coord[0]]
    else:
        return getvalue(coord[1:],board[coord[0]])

def setvalue(coord,board,value):
    '''Sets value of coord element in board to value'''
    if(len(coord)==1):
        board[coord[0]] = value
    else:
        setvalue(coord[1:],board[coord[0]],value)

def counter(dimensions,board,value):
    '''Returns Number of points in nested list board with dimensions of certain value'''
    if (len(dimensions)==1):
        count=0
        for i in range(dimensions[0]):
            if(board[i]==value):
                count+=1
        return count
    else:
        count=0
        for i in range(dimensions[0]):
            count+=counter(dimensions[1:],board[i],value)
        return count

def cells(dimensions):
    '''Number of points in nested list with dimensions dimensions'''
    counter=1
    for i in range(len(dimensions)):
        counter=counter*dimensions[i]
    return counter



def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board', 'bombs' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    bombs: [(0, 0, 1), (1, 0, 0), (1, 1, 1)]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    
    """
    board=[]
    visible=[]
    
    makearray(dimensions,board,0) # Makes all elements of each board and visible and initliazes value
    makearray(dimensions,visible,False)
    for b in bombs:
        setvalue(b,board,'.')
    def updateneighbors(coordinates,board,dimensions):
        '''Adds 1 to board element for each non-bomb neighbor of a bomb'''
        if(len(coordinates)==1): # If last coordinate, check each possibility and then add 1
            r=coordinates[0]
            if(0<=r-1<=dimensions[0]-1):
                if(board[r-1]!='.'):
                    board[r-1]+=1
            if(0<=r<=dimensions[0]-1):
                if(board[r]!='.'):  
                    board[r]+=1
            if(0<=r+1<=dimensions[0]-1):
                if(board[r+1]!='.'):  
                    board[r+1]+=1
        else:
            r=coordinates[0] # Take first element and check each possibility.
            if(0<=r-1<=dimensions[0]-1):
                updateneighbors(coordinates[1:],board[r-1],dimensions[1:]) # Updateneighbors again now including new possibilities for r  
            if(0<=r<=dimensions[0]-1):
                updateneighbors(coordinates[1:],board[r],dimensions[1:])  
            if(0<=r+1<=dimensions[0]-1):
                updateneighbors(coordinates[1:],board[r+1],dimensions[1:])
    for b in bombs:
        updateneighbors(b,board,dimensions)
    
    return {
        'dimensions': dimensions,
        'board': board,
        'visible': visible,
        'state': 'ongoing',
        'bombs':bombs}



def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing', 'bombs':[(0, 0, 1), (1, 0, 0), (1, 1, 1)]}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    bombs: [(0, 0, 1), (1, 0, 0), (1, 1, 1)]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing', 'bombs': [(0, 0, 1), (1, 0, 0), (1, 1, 1)]}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    bombs: [(0, 0, 1), (1, 0, 0), (1, 1, 1)]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    
    number=cells(game['dimensions'])
    if game['state'] == 'defeat' or game['state'] == 'victory': # Keep defined state the same
        return 0

    if getvalue(coordinates,game['board']) == '.': # Lose and reveal if bomb selected
        setvalue(coordinates,game['visible'],True)
        game['state'] = 'defeat'
        return 1

    if getvalue(coordinates,game['visible']) == True: # Move causes no change
        return 0    

    setvalue(coordinates,game['visible'],True)
    revealed = 1

    count=counter(game['dimensions'],game['visible'],True) 
    if count == number-len(game['bombs']): # All non-bombs space are visible, so game won
        game['state'] = 'victory'
        return 1

    def allneighbors(coord,path):
        ''' Constructs all neighbors of coord and runs dig on valid ones'''
        opened=0
        if(len(coord)==1):
            for i in [-1,0,1]: # check all 3 directions
                if(0<=coord[0]+i<game['dimensions'][len(path)]): 
                    a=path[:]
                    a.append(coord[0]+i)
                else:
                    continue
                if getvalue(a,game['visible'])==False: # Dig if not found
                    if(getvalue(a,game['board'])==0):
                        k=dig_nd(game,a)
                    else:
                        setvalue(a,game['visible'],True)
                        k=1
                else:
                    k=0        
                opened+=k # Keep track of spaces revealed
            return opened
        else:
            for i in [-1,0,1]:
                if(0<=coord[0]+i<game['dimensions'][len(path)]):
                    a=path[:]
                    a.append(coord[0]+i) # New path with next coordinate possibility accounted for
                    k=allneighbors(coord[1:],a)
                    opened+=k
            return opened


    if getvalue(coordinates,game['board']) == 0:
        revealed+=allneighbors(coordinates,[])    
    
    totalfalse = counter(game['dimensions'],game['visible'],False)
    covered_squares=totalfalse-len(game['bombs'])
    if covered_squares > 0: # Exists a non-bomb square that is not visible
        game['state'] = 'ongoing'
        return revealed
    else:
        game['state'] = 'victory'
        return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    
    board = []
    makearray(game['dimensions'],board,'_')
    def makecoord(path):
        ''' Creates all coordinates and checks value'''
        n=len(path)
        if(len(path)==len(game['dimensions'])):
            if(xray or getvalue(path,game['visible'])==True):
                c=getvalue(path,game['board'])
                if(c=='.'):
                       setvalue(path,board,'.')
                elif(c==0):
                    setvalue(path,board,' ')
                else:
                    setvalue(path,board,str(c))
        else:
            for i in range(game['dimensions'][len(path)]):
                a=path[:]
                a.append(i)
                makecoord(a)
    makecoord([])
    return board



if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
