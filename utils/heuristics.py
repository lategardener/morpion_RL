import numpy as np
from configs.config import REWARD_CREATE_THREAT, REWARD_ALLOW_OPP_WIN

def win_on_line(number_line, pattern, board, pattern_length):
    """
    Check if there is a winning sequence on a specific horizontal line.

    Args:
        number_line (int): Index of the line to check.
        pattern (int): The player pattern to check (e.g., 0 or 1).
        board (np.ndarray): The game board as a 2D array.
        pattern_length (int): The required consecutive pattern length to win.

    Returns:
        bool: True if winning pattern is found on the line, else False.
    """
    # Convert the line to a string of cell values
    line_str = "".join(str(int(cell)) for cell in board[number_line])
    # Check if the winning pattern is in the line string
    return str(pattern) * pattern_length in line_str


def win_on_column(number_column, pattern, board, pattern_length):
    """
    Check if there is a winning sequence on a specific vertical column.

    Args:
        number_column (int): Index of the column to check.
        pattern (int): The player pattern to check.
        board (np.ndarray): The game board.
        pattern_length (int): The required consecutive pattern length to win.

    Returns:
        bool: True if winning pattern is found on the column, else False.
    """
    # Extract the column cells and convert to string
    column_str = "".join(str(int(row[number_column])) for row in board)
    # Check for winning pattern in the column string
    return str(pattern) * pattern_length in column_str


def win_on_descending_diagonal(length, x, y, pattern, board, pattern_length):
    """
    Check for a winning sequence on the descending diagonal (top-left to bottom-right)
    passing through the cell (x, y).

    Args:
        length (int): Board size (length x length).
        x (int): Row index of the cell.
        y (int): Column index of the cell.
        pattern (int): Player pattern to check.
        board (np.ndarray): The game board.
        pattern_length (int): The required consecutive pattern length to win.

    Returns:
        bool: True if winning pattern is found on this diagonal, else False.
    """
    diagonal = ""

    # Move to the top-left along the diagonal
    i, j = x, y
    while i >= 0 and j >= 0:
        diagonal = str(int(board[i][j])) + diagonal
        i -= 1
        j -= 1

    # Move to the bottom-right along the diagonal
    i, j = x + 1, y + 1
    while i < length and j < length:
        diagonal += str(int(board[i][j]))
        i += 1
        j += 1

    # Check for winning pattern in diagonal string
    return str(pattern) * pattern_length in diagonal


def win_on_ascending_diagonal(length, x, y, pattern, board, pattern_length):
    """
    Check for a winning sequence on the ascending diagonal (bottom-left to top-right)
    passing through the cell (x, y).

    Args:
        length (int): Board size.
        x (int): Row index of the cell.
        y (int): Column index of the cell.
        pattern (int): Player pattern to check.
        board (np.ndarray): The game board.
        pattern_length (int): Required consecutive pattern length to win.

    Returns:
        bool: True if winning pattern is found on this diagonal, else False.
    """
    diagonal = ""

    # Move to bottom-left along the ascending diagonal
    i, j = x, y
    while i < length and j >= 0:
        diagonal = str(int(board[i][j])) + diagonal
        i += 1
        j -= 1

    # Move to top-right along the diagonal
    i, j = x - 1, y + 1
    while i >= 0 and j < length:
        diagonal += str(int(board[i][j]))
        i -= 1
        j += 1

    # Check for winning pattern in diagonal string
    return str(pattern) * pattern_length in diagonal


def board_is_full(board):
    """
    Check if the board is completely filled (no empty cells).

    Args:
        board (np.ndarray): The game board.

    Returns:
        bool: True if the board has no empty cells, False otherwise.
    """
    # EMPTY_CELL is 3, so ensure no cell equals 3
    return all(all(int(cell) != 3 for cell in row) for row in board)







# ------------------------- OPENED THREATS ------------------------------------

def number_of_opened_threats_on_rows(threat_length, playerId, board):
    """
    Count the number of opened threats of a given length for a player on all rows.
    An opened threat is defined as the pattern: empty cell + consecutive player marks + empty cell,
    where empty cell is represented by '3'.

    Args:
        threat_length (int): Length of the threat pattern (number of consecutive player marks).
        playerId (str): Player ID as a string ('0' or '1').
        board (np.ndarray): 2D game board.

    Returns:
        int: Total number of opened threats found on all rows.
    """
    count = 0
    for row in board:
        # Convert the row into a string for pattern matching
        row_str = "".join([str(int(elt)) for elt in row])
        pattern = "3" + playerId * threat_length + "3"  # Pattern to find
        start = 0
        while True:
            # Find pattern starting from current index
            start = row_str.find(pattern, start)
            if start == -1:
                break
            count += 1
            # Move start index past the current pattern, minus overlapping 2 chars to allow overlapping matches
            start += len(pattern) - 2
    return count


def number_of_opened_threats_on_columns(threat_length, playerId, board, size):
    """
    Count the number of opened threats of a given length for a player on all columns.

    Args:
        threat_length (int): Length of the threat pattern.
        playerId (str): Player ID as a string.
        board (np.ndarray): 2D game board.
        size (int): Board size (number of rows/columns).

    Returns:
        int: Total number of opened threats found on all columns.
    """
    count = 0
    for column_number in range(size):
        # Extract the column as a string for pattern matching
        column_str = "".join([str(int(board[row_number][column_number])) for row_number in range(size)])
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            start = column_str.find(pattern, start)
            if start == -1:
                break
            count += 1
            start += len(pattern) - 2
    return count


def number_of_opened_threats_on_descending_diagonals(threat_length, playerId, board, size):
    """
    Count the number of opened threats on all descending diagonals (top-left to bottom-right)
    for a given player.

    Args:
        threat_length (int): Length of the threat pattern.
        playerId (str): Player ID as a string.
        board (np.ndarray): 2D game board.
        size (int): Board size.

    Returns:
        int: Total number of opened threats found on all descending diagonals.
    """
    count = 0

    # Check descending diagonals starting from first row
    for x in range(size):
        diagonal_str = ""
        i, j = x, 0
        while i < size and j < size:
            diagonal_str += str(int(board[i][j]))
            i += 1
            j += 1
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            start = diagonal_str.find(pattern, start)
            if start == -1:
                break
            count += 1
            start += len(pattern) - 2

    # Check descending diagonals starting from first column (except the top-left corner, already checked)
    for y in range(1, size):
        diagonal_str = ""
        i, j = 0, y
        while i < size and j < size:
            diagonal_str += str(int(board[i][j]))
            i += 1
            j += 1
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            start = diagonal_str.find(pattern, start)
            if start == -1:
                break
            count += 1
            start += len(pattern) - 2

    return count


def number_of_opened_threats_on_ascending_diagonals(threat_length, playerId, board, size):
    """
    Count the number of opened threats on all ascending diagonals (bottom-left to top-right)
    for a given player.

    Args:
        threat_length (int): Length of the threat pattern (consecutive player marks).
        playerId (str): Player ID as a string ('0' or '1').
        board (np.ndarray): 2D game board.
        size (int): Board size.

    Returns:
        int: Total number of opened threats found on all ascending diagonals.
    """
    count = 0

    # Check ascending diagonals starting from the last row
    for x in range(size):
        diagonal_str = ""
        i, j = x, 0
        while i >= 0 and j < size:
            diagonal_str += str(int(board[i][j]))
            i -= 1
            j += 1

        pattern = "3" + playerId * threat_length + "3"  # Pattern to find
        start = 0
        while True:
            start = diagonal_str.find(pattern, start)
            if start == -1:
                break
            count += 1
            # Move past the found pattern with some overlap allowed
            start += len(pattern) - 2

    # Check ascending diagonals starting from the first column (except bottom-left corner)
    for y in range(1, size):
        diagonal_str = ""
        i, j = size - 1, y
        while i >= 0 and j < size:
            diagonal_str += str(int(board[i][j]))
            i -= 1
            j += 1

        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            start = diagonal_str.find(pattern, start)
            if start == -1:
                break
            count += 1
            start += len(pattern) - 2

    return count


def number_of_opened_threats(threat_length, playerId, board, size):
    """
    Aggregate the count of opened threats across all directions:
    rows, columns, descending diagonals, and ascending diagonals.

    Args:
        threat_length (int): Length of the threat pattern.
        playerId (str): Player ID as a string.
        board (np.ndarray): 2D game board.
        size (int): Board size.

    Returns:
        int: Total number of opened threats found in the board.
    """
    return (number_of_opened_threats_on_rows(threat_length, playerId, board) +
            number_of_opened_threats_on_columns(threat_length, playerId, board, size) +
            number_of_opened_threats_on_descending_diagonals(threat_length, playerId, board, size) +
            number_of_opened_threats_on_ascending_diagonals(threat_length, playerId, board, size))


# ------------------------- SEMI-OPENED THREATS ------------------------------------

def pattern_(playerId, length, opponentId, pattern_victory_length):
    """
    Generate patterns representing semi-opened threat configurations for the given player.

    Args:
        playerId (str): Player's ID as a string (e.g., '0' or '1').
        length (int): Length of the consecutive marks to form a threat.
        opponentId (str): Opponent's ID as a string.
        pattern_victory_length (int): Number of consecutive marks required to win.

    Returns:
        tuple:
            - List of all semi-opened threat patterns.
            - List of 'wall-blocked' threat patterns (threats blocked by player's own marks at edges).
            - List of special semi-opened threat patterns enclosed by empty cells ("3").
    """
    from itertools import permutations

    # Base data: consecutive player marks + one empty cell "3"
    data = [playerId for _ in range(length)] + ["3"]

    # Generate all unique permutations of the base data
    all_permutations = set(permutations(data))

    filtered_permutations = [list(p) for p in all_permutations]

    # Wall-blocked threats: patterns starting and ending with playerId (fully blocked on both ends)
    wall_blocked = [threat for threat in filtered_permutations if threat[0] == playerId and threat[-1] == playerId]
    wall_blocked = ["".join(threat) for threat in wall_blocked] + [
        playerId * length + "3" * (pattern_victory_length - length),
        "3" * (pattern_victory_length - length) + playerId * length
    ]

    # Special patterns enclosed by empty cells ("3")
    filtered_permutations_specials = [["3"] + l + ["3"] for l in filtered_permutations if l[0] == playerId and l[-1] == playerId]

    # Patterns with opponentId blocking on one side and empty cells on the other
    filtered_permutations_two = [["3" * (pattern_victory_length - len(l))] + l + [opponentId] for l in filtered_permutations if l[0] == playerId and l[-1] == playerId]
    filtered_permutations_three = [[opponentId] + l + ["3" * (pattern_victory_length - len(l))] for l in filtered_permutations if l[0] == playerId and l[-1] == playerId]

    # Combine all filtered patterns into a single list
    filtered_permutations = (
            filtered_permutations_two +
            filtered_permutations_three +
            # The following commented-out patterns can be added if needed
            # filtered_permutations_four +
            [[symbol for symbol in opponentId + length * playerId + "3" * (pattern_victory_length - length)]] +
            [[symbol for symbol in "3" * (pattern_victory_length - length) + length * playerId + opponentId]]
    )
    filtered_permutations = ["".join(threat) for threat in filtered_permutations]

    return filtered_permutations, wall_blocked, ["".join(threat) for threat in filtered_permutations_specials]


def contains_all_semi_opened_threats(segment, threat_length, playerId, opponentId, pattern_victory_length):
    """
    Counts how many semi-opened threat patterns are contained in a given board segment (string).

    Args:
        segment (str): Segment of the board represented as a string.
        threat_length (int): Length of the threat pattern (consecutive player marks).
        playerId (str): Player's ID as a string.
        opponentId (str): Opponent's ID as a string.
        pattern_victory_length (int): Number of consecutive marks required to win.

    Returns:
        int: Total count of detected semi-opened threat patterns in the segment.
    """
    # Generate all semi-opened threat patterns and wall-blocked patterns
    patterns, wall_blocked, _ = pattern_(playerId, threat_length, opponentId, pattern_victory_length)

    pattern_find_on_the_left = False
    pattern_find_on_the_right = False

    total_count = 0

    # Search for each pattern in the segment
    for pattern in patterns:
        start = 0
        while True:
            start = segment.find(pattern, start)
            if start == -1:
                break
            total_count += 1

            # Check if pattern is at the start of the segment
            if start == 0:
                pattern_find_on_the_left = True
            # Check if pattern is at the end of the segment
            if start + len(pattern) == len(segment):
                pattern_find_on_the_right = True

            start += 1  # Advance to avoid infinite loop

    # Additional checks for wall-blocked patterns if no pattern found at segment edges
    if not pattern_find_on_the_left:
        for pattern in wall_blocked:
            if pattern[0] == playerId and segment.startswith(pattern):
                total_count += 1
                if len(pattern) == len(segment):
                    return total_count
                break

    if not pattern_find_on_the_right:
        for pattern in wall_blocked:
            if pattern[-1] == playerId and segment.endswith(pattern):
                total_count += 1
                break

    return total_count


def contains_dangerous_semi_opened_threats(segment, threat_length, playerId, opponentId, pattern_victory_length):
    """
    Counts occurrences of dangerous semi-opened threat patterns in a board segment.

    Args:
        segment (str): Board segment represented as a string.
        threat_length (int): Length of threat pattern (consecutive player marks).
        playerId (str): Player's ID as string.
        opponentId (str): Opponent's ID as string.
        pattern_victory_length (int): Number of consecutive marks needed to win.

    Returns:
        int: Total count of dangerous semi-opened threats found in the segment.
    """
    # Retrieve only the dangerous semi-opened threat patterns from pattern_ function
    _, _, dangerous_pattern = pattern_(playerId, threat_length, opponentId, pattern_victory_length)

    total_count = 0

    # Search for each dangerous pattern within the segment string
    for pattern in dangerous_pattern:
        start = 0
        while True:
            start = segment.find(pattern, start)
            if start == -1:
                break
            total_count += 1
            start += 1  # Advance index to avoid infinite loops

    return total_count


def number_of_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length):
    """
    Counts all semi-opened threats on each row of the board.

    Args:
        threat_length (int): Length of threat pattern.
        playerId (str): Player's ID.
        opponentId (str): Opponent's ID.
        board (list): 2D list or numpy array representing the board.
        pattern_victory_length (int): Number of consecutive marks required to win.

    Returns:
        int: Total number of semi-opened threats found on rows.
    """
    count = 0
    for row in board:
        row_str = "".join([str(int(elt)) for elt in row])
        count += contains_all_semi_opened_threats(row_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count


def number_of_dangerous_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length):
    """
    Counts dangerous semi-opened threats on each row of the board.

    Args and Returns same as above.
    """
    count = 0
    for row in board:
        row_str = "".join([str(int(elt)) for elt in row])
        count += contains_dangerous_semi_opened_threats(row_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count


def number_of_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Counts all semi-opened threats on each column of the board.

    Args and Returns similar to rows function, with board size.
    """
    count = 0
    for column_number in range(size):
        column_str = "".join([str(int(elt[column_number])) for elt in board])
        count += contains_all_semi_opened_threats(column_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count


def number_of_dangerous_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Counts dangerous semi-opened threats on each column of the board.

    Args and Returns similar to above.
    """
    count = 0
    for column_number in range(size):
        column_str = "".join([str(int(elt[column_number])) for elt in board])
        count += contains_dangerous_semi_opened_threats(column_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count


def number_of_semi_opened_threats_on_descending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Counts all semi-opened threats on each descending diagonal of the board.

    Args and Returns similar to above.
    """
    count = 0
    # Descending diagonals starting from first row
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        while i < size and j < size:
            diagonal += str(int(board[i][j]))
            i += 1
            j += 1
        count += contains_all_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    # Descending diagonals starting from first column (excluding the main diagonal already counted)
    for y in range(1, size):
        diagonal = ""
        i, j = 0, y
        while i < size and j < size:
            diagonal += str(int(board[i][j]))
            i += 1
            j += 1
        count += contains_all_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    return count


def number_of_dangerous_semi_opened_threats_on_descending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Counts dangerous semi-opened threats on all descending diagonals of the board.

    Args:
        threat_length (int): Length of threat pattern.
        playerId (str): Player's ID.
        opponentId (str): Opponent's ID.
        board (list): 2D board representation.
        size (int): Board size (length).
        pattern_victory_length (int): Number of consecutive marks to win.

    Returns:
        int: Total count of dangerous semi-opened threats on descending diagonals.
    """
    count = 0
    # Iterate over diagonals starting from first row
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        # Traverse downward right diagonal
        while i < size and j < size:
            diagonal += str(int(board[i][j]))
            i += 1
            j += 1
        # Count dangerous semi-opened threats in this diagonal segment
        count += contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    # Iterate over diagonals starting from first column (excluding main diagonal)
    for y in range(1, size):
        diagonal = ""
        i, j = 0, y
        # Traverse downward right diagonal
        while i < size and j < size:
            diagonal += str(int(board[i][j]))
            i += 1
            j += 1
        count += contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    return count


def number_of_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Counts all semi-opened threats on ascending diagonals of the board.

    Args and returns same as above.
    """
    count = 0
    # Iterate over diagonals starting from last row
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        # Traverse upward right diagonal
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        # Count all semi-opened threats in this diagonal segment
        count += contains_all_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    # Iterate over diagonals starting from first column (excluding main diagonal)
    for y in range(1, size):
        diagonal = ""
        i, j = size - 1, y
        # Traverse upward right diagonal
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        count += contains_all_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    return count


def number_of_dangerous_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Counts dangerous semi-opened threats on ascending diagonals of the board.

    Args and returns same as above.
    """
    count = 0
    # Iterate over diagonals starting from last row
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        # Traverse upward right diagonal
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        # Count dangerous semi-opened threats in this diagonal segment
        count += contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    # Iterate over diagonals starting from first column (excluding main diagonal)
    for y in range(1, size):
        diagonal = ""
        i, j = size - 1, y
        # Traverse upward right diagonal
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        count += contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    return count


def number_of_semi_opened_threats(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Calculate total number of semi-opened threats for a player across the board.
    Sums threats found on rows, columns, descending and ascending diagonals.
    """
    return (
            number_of_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length) +
            number_of_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_semi_opened_threats_on_descending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length)
    )


def number_of_dangerous_semi_opened_threats(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    """
    Calculate total number of dangerous semi-opened threats for a player across the board.
    Sums dangerous threats found on rows, columns, descending and ascending diagonals.
    """
    return (
            number_of_dangerous_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length) +
            number_of_dangerous_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_dangerous_semi_opened_threats_on_descending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_dangerous_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length)
    )


def threats_without_holes(playerId, board, size, pattern_victory_length):
    """
    Counts the number of winning threat patterns (without gaps) for a player on the board.
    Checks all rows, columns, and both diagonals.
    """
    count = 0
    for i in range(size):
        count += (
                win_on_line(i, playerId, board, pattern_victory_length) +
                win_on_column(i, playerId, board, pattern_victory_length) +
                win_on_descending_diagonal(size, i, 0, playerId, board, pattern_victory_length) +
                win_on_ascending_diagonal(size, i, 0, playerId, board, pattern_victory_length)
        )
        if i > 0:
            count += win_on_ascending_diagonal(size, size - 1, i, playerId, board, pattern_victory_length)
            count += win_on_descending_diagonal(size, 0, i, playerId, board, pattern_victory_length)
    return count


def won_in_next_move(playerId, board, size, pattern_victory_length, move):
    """
    Simulates a move by the player and checks if it creates a winning threat pattern.
    Returns the move if it results in a win next turn, otherwise None.
    """
    line, column = divmod(move, size)
    board[line][column] = playerId
    if threats_without_holes(playerId, board, size, pattern_victory_length) > 0:
        return move
    return None


def is_winning_move(playerId, board, size, pattern_victory_length, authorized_moves):
    """
    Iterates over authorized moves to check if any move leads to an immediate win.
    Returns the winning move if found, else None.
    """
    for move in authorized_moves:
        result = won_in_next_move(playerId, board.copy(), size, pattern_victory_length, move)
        if result is not None:
            return result
    return None


# -------------------------------------- HEURISTIC -----------------------------------------

def opponent_heuristic_points_calcul(opponentId, playerId, board, size, length_victory_pattern):
    """
    Calculate the heuristic score based on the opponent's threats on the board.

    The score is a weighted sum of:
    - Semi-opened threats (length - 2)
    - Dangerous semi-opened threats (length - 2)
    - Opened threats (length - 2)
    """
    score = 0
    score += (
            0.05 * number_of_semi_opened_threats(length_victory_pattern - 2, opponentId, playerId, board, size, length_victory_pattern) +
            0.1 * number_of_dangerous_semi_opened_threats(length_victory_pattern - 2, opponentId, playerId, board, size, length_victory_pattern) +
            1.2 * number_of_opened_threats(length_victory_pattern - 2, opponentId, board, size)
    )
    return score


def agent_heuristic_points_calcul(playerId, opponentId, board, size, length_victory_pattern):
    """
    Calculate the heuristic score based on the agent's own threats on the board.

    The score is a weighted sum of:
    - Semi-opened threats (length - 2)
    - Dangerous semi-opened threats (length - 2)
    - Opened threats (length - 2)
    - Semi-opened threats (length - 1)
    - Dangerous semi-opened threats (length - 1)
    - Opened threats (length - 1)
    """
    score = 0
    score += (
            0.05 * number_of_semi_opened_threats(length_victory_pattern - 2, playerId, opponentId, board, size, length_victory_pattern) +
            0.1 * number_of_dangerous_semi_opened_threats(length_victory_pattern - 2, playerId, opponentId, board, size, length_victory_pattern) +
            1.2 * number_of_opened_threats(length_victory_pattern - 2, playerId, board, size) +
            2 * number_of_semi_opened_threats(length_victory_pattern - 1, playerId, opponentId, board, size, length_victory_pattern) +
            2 * number_of_dangerous_semi_opened_threats(length_victory_pattern - 1, playerId, opponentId, board, size, length_victory_pattern) +
            3 * number_of_opened_threats(length_victory_pattern - 1, playerId, board, size)
    )
    return score


def heuristic_points(playerId, opponentId, board, size, length_victory_pattern, authorized_moves):
    """
    Evaluate heuristic reward or penalty based on immediate winning moves:
    - If opponent has a winning move available, return penalty (REWARD_ALLOW_OPP_WIN).
    - If agent has a winning move available, return bonus (REWARD_CREATE_THREAT).
    - Otherwise, return zero.
    """
    if is_winning_move(opponentId, board, size, length_victory_pattern, authorized_moves) is not None:
        return REWARD_ALLOW_OPP_WIN

    bonus = 0
    if is_winning_move(playerId, board, size, length_victory_pattern, authorized_moves):
        bonus = REWARD_CREATE_THREAT
    return bonus


def estimate_heuristic_bounds(board_size, length_victory_pattern):
    """
    Estimate minimum and maximum heuristic score bounds based on board size and winning pattern length.

    Parameters:
    - board_size: size of the board (e.g., 3 for classic tic-tac-toe)
    - length_victory_pattern: length of the winning pattern

    Returns:
    - (min_heuristic, max_heuristic): tuple representing the bounds of heuristic values
    """
    # Placeholder heuristic bounds; adjust based on specific weighting and board configuration
    max_heuristic = 10000
    min_heuristic = 0
    return min_heuristic, max_heuristic


def normalize(value, board_size, length_victory_pattern):
    """
    Normalize a heuristic value to a 0-1 scale based on estimated heuristic bounds.

    Parameters:
    - value: heuristic value to normalize
    - board_size: size of the board
    - length_victory_pattern: length of the winning pattern

    Returns:
    - Normalized value between 0 and 1
    """
    min_val, max_val = estimate_heuristic_bounds(board_size, length_victory_pattern)
    return (value - min_val) / (max_val - min_val)



























