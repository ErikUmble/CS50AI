"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

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
    num_x_moves = 0
    num_o_moves = 0

    # Count up moves completed
    for row in board:
        for column in row:
            if column == X:
                num_x_moves += 1
            elif column == O:
                num_o_moves += 1

    # If their moves are equal, it is X's turn, otherwise it is O's turn
    if num_x_moves == num_o_moves:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()

    # Iterate through the board, keeping track of open positions
    for i,row in enumerate(board):
        for j,cell in enumerate(row):
            if cell == EMPTY:
                possible_actions.add((i,j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] is not EMPTY:
        raise Exception

    resulting_board = deepcopy(board)
    resulting_board[action[0]][action[1]] = player(board)

    return resulting_board
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows and columns
    for i in range(3):
        
        # Check row for 3 identical (and that it is not an empty row)
        if board[i][0] is not EMPTY and board[i][0] == board[i][1] and board[i][0] == board[i][2]:
            return board[i][0]
        
        # Check col for 3 identical
        if board[0][i] is not EMPTY and board[0][i] == board[1][i] and board[0][i] == board[2][i]:
            return board[0][i]
        
    # Check diagonals
    if board[0][0] is not EMPTY and board[0][0] == board[1][1] and board[0][0] == board[2][2]:
        return board[0][0]
    
    if board[0][2] is not EMPTY and board[0][2] == board[1][1] and board[0][2] == board[2][0]:
        return board[0][2]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if len(actions(board)) == 0:
        return True

    if winner(board) is None:
        return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    won_by = winner(board)
    if won_by == X:
        return 1

    elif won_by == O:
        return -1

    return 0


def max_value(board, terminal_checked = False):
    """
    :param board:
    :return: the maximum value of results possible from the board assuming optimal play
    """

    if not terminal_checked and terminal(board):
        return utility(board)

    v = -2
    # Try the path along each action, assuming the next play will seek to minimize the score
    for action in actions(board):
        v = max(v, min_value(result(board, action)))

    return v


def min_value(board, terminal_checked = False):
    """
    :param board:
    :return: the minimum value of results possible from the board assuming optimal play
    :parameter terminal_checked: if the board has been checked for terminality already
    """

    if not terminal_checked and terminal(board):
        return utility(board)

    v = 2
    # Try the path along each action, assuming the next play will seek to minimize the score
    for action in actions(board):
        v = min(v, max_value(result(board, action)))

    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    possible_actions = actions(board)
    # Keep track of best action
    best_action = None

    if player(board) == X:
        highest_score = -2
        for action in possible_actions:
            resulting_score = min_value(result(board, action))

            # update best action if necessary
            if resulting_score > highest_score:
                highest_score = resulting_score
                best_action = action
    else:
        lowest_score = 2
        for action in possible_actions:
            resulting_score = max_value(result(board, action))

            # update best action if necessary
            if resulting_score < lowest_score:
                lowest_score = resulting_score
                best_action = action

    return best_action


if __name__ == '__main__':
    test_board = [[EMPTY, EMPTY, X],
                  [O, O, X],
                  [O, EMPTY, X]]

    print(winner(test_board))
    print(minimax(test_board))