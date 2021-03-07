"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
import random

X = "X" 
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]



def player(board):
    """
    Returns player who has the next turn on a board.
    """
    counter = 0
    for row in board:
        for col in row:
            if col == X or col == O:
                counter += 1
    if counter % 2 == 0:
        return X 
    return O 


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for row in range(3):
        for col in range(3):
            if board[row][col] == EMPTY:
                actions.add((row, col))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    row, col = action 
    player_next = player(board)
    board_next = deepcopy(board)
    allowed_actions = actions(board)

    try:
        assert action in allowed_actions
        board_next[row][col] = player_next
        return board_next
    except:
        raise Exception("not a valid move.")






def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # I can check the entire board from 5 main points
    # Point 1:
    val = board[0][0]
    if board[0][1] == val and board[0][2] == val:
        return val 
    
    if board[1][0] == val and board[2][0] == val:
        return val 
    
    if board[1][1] == val and board[2][2] == val:
        return val 

    # Point 2:
    val = board[0][1]
    if board[1][1] == val and board[2][1] == val:
        return val 

    # Point 3:
    val = board[0][2]
    if board[1][2] == val and board[2][2] == val:
        return val 
    
    if board[1][1] == val and board[2][0] == val:
        return val 

    # Point 4:
    val = board[1][0]
    if board[1][1] == val and board[1][2] == val:
        return val 

    # Point 5:
    val = board[2][0]
    if board[2][1] == val and board[2][2] == val:
        return val 
    
    return None 
    


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    won = winner(board)
    draw = True 
    for row in board:
        if EMPTY in row:
            draw = False 
    
    if won or draw:
        return True 
    return False 


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    won = winner(board)
    if won == X:
        return 1
    elif won == O:
        return -1
    return 0


def max_value(board):
    v = - math.inf
    if terminal(board):
        return utility(board)
    
    possible_actions = actions(board)
    for action in possible_actions:
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    v = math.inf
    if terminal(board):
        return utility(board)
    
    possible_actions = actions(board)
    for action in possible_actions:
        v = min(v, max_value(result(board, action)))
    return v 


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if board == initial_state():
        return (random.randint(0,2), random.randint(0,2))

    if terminal(board):
        return None 

    turn = player(board)
    possible_actions = actions(board)
    actions_values = dict()
    if turn == X:
        for action in possible_actions:
            value = min_value(result(board, action))
            actions_values[action] = value
        sort = sorted(actions_values.keys(), key = lambda x: actions_values[x], reverse = True)
    
    elif turn == O:
        for action in possible_actions:
            value = max_value(result(board, action))
            actions_values[action] = value 
        sort = sorted(actions_values.keys(), key = lambda x: actions_values[x])
    
    return sort[0]
    
