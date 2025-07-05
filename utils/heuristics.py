import numpy as np

def win_on_line(number_line, pattern, board, pattern_length):
    list_ = [str(int(elt)) for elt in board[number_line]]
    concatenation = "".join(list_)
    return str(pattern) * pattern_length in concatenation


def win_on_column(number_column, pattern, board, pattern_length):
    list_ = [str(int(elt[number_column])) for elt in board]
    concatenation = "".join(list_)
    return str(pattern) * pattern_length in concatenation


def win_on_descending_diagonal(length, x, y, pattern, board, pattern_length):
    diagonal = ""

    i, j = x, y
    while i >= 0 and j >= 0:
        diagonal = str(int(str(int(board[i][j])))) + diagonal
        i -= 1
        j -= 1

    i, j = x + 1, y + 1
    while i < length and j < length:
        diagonal += str(int(str(int(board[i][j]))))
        i += 1
        j += 1

    return str(pattern) * pattern_length in diagonal

def win_on_ascending_diagonal(length, x, y, pattern, board, pattern_length):
    diagonal = ""

    i, j = x, y
    while i < length and j >= 0:
        diagonal = str(int(str(int(board[i][j])))) + diagonal
        i += 1
        j -= 1

    i, j = x - 1, y + 1
    while i >= 0 and j < length:
        diagonal += str(int(str(int(board[i][j]))))
        i -= 1
        j += 1

    return str(pattern) * pattern_length in diagonal

def board_is_full(board):
    return all(all(int(box) != 3 for box in line) for line in board)


""" -------------------------------------------------------------------------------------------------------"""






# ------------------------- OPENED THREATS ------------------------------------

def number_of_opened_threats_on_rows(threat_length, playerId, board):
    count = 0
    for row in board:
        row_str = "".join([str(int(elt)) for elt in row])
        # Motif de menace ouverte à rechercher
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            start = row_str.find(pattern, start)
            if start == -1:
                break
            count += 1
            start += len(pattern) - 2
    return count

def number_of_opened_threats_on_columns(threat_length, playerId, board, size):
    count = 0
    for column_number in range(size):
        column_str = "".join([str(int(board[row_number][column_number])) for row_number in range(size)])
        # Motif de menace ouverte à rechercher
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            # Trouve la position du motif dans la chaîne
            start = column_str.find(pattern, start)
            if start == -1:
                # Aucune autre occurrence trouvée, on arrête la boucle
                break
            count += 1
            # Continue la recherche à partir de la position juste après la fin du motif trouvé
            start += len(pattern) - 2
    return count

def number_of_opened_threats_on_descending_diagonals(threat_length, playerId, board, size):
    count = 0
    # Descend les diagonales à partir de la première ligne
    for x in range(size):
        diagonal_str = ""
        i, j = x, 0
        while i < size and j < size:
            diagonal_str += str(int(board[i][j]))
            i += 1
            j += 1
        # Motif de menace ouverte à rechercher
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            # Trouve la position du motif dans la chaîne
            start = diagonal_str.find(pattern, start)
            if start == -1:
                # Aucune autre occurrence trouvée, on arrête la boucle
                break
            count += 1
            # Continue la recherche à partir de la position juste après la fin du motif trouvé
            start += len(pattern) - 2

    # Descend les diagonales à partir de la première colonne
    for y in range(1, size):
        diagonal_str = ""
        i, j = 0, y
        while i < size and j < size:
            diagonal_str += str(int(board[i][j]))
            i += 1
            j += 1
        # Motif de menace ouverte à rechercher
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            # Trouve la position du motif dans la chaîne
            start = diagonal_str.find(pattern, start)
            if start == -1:
                # Aucune autre occurrence trouvée, on arrête la boucle
                break
            count += 1
            # Continue la recherche à partir de la position juste après la fin du motif trouvé
            start += len(pattern) - 2

    return count

def number_of_opened_threats_on_ascending_diagonals(threat_length, playerId, board, size):
    count = 0
    # Ascend les diagonales à partir de la dernière ligne
    for x in range(size):
        diagonal_str = ""
        i, j = x, 0
        while i >= 0 and j < size:
            diagonal_str += str(int(board[i][j]))
            i -= 1
            j += 1
        # Motif de menace ouverte à rechercher
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            # Trouve la position du motif dans la chaîne
            start = diagonal_str.find(pattern, start)
            if start == -1:
                # Aucune autre occurrence trouvée, on arrête la boucle
                break
            count += 1
            # Continue la recherche à partir de la position juste après la fin du motif trouvé
            start += len(pattern) - 2

    # Ascend les diagonales à partir de la première colonne
    for y in range(1, size):
        diagonal_str = ""
        i, j = size - 1, y
        while i >= 0 and j < size:
            diagonal_str += str(int(board[i][j]))
            i -= 1
            j += 1
        # Motif de menace ouverte à rechercher
        pattern = "3" + playerId * threat_length + "3"
        start = 0
        while True:
            # Trouve la position du motif dans la chaîne
            start = diagonal_str.find(pattern, start)
            if start == -1:
                # Aucune autre occurrence trouvée, on arrête la boucle
                break
            count += 1
            # Continue la recherche à partir de la position juste après la fin du motif trouvé
            start += len(pattern) - 2

    return count

def number_of_opened_threats(threat_length, playerId, board, size):
    return (number_of_opened_threats_on_rows(threat_length, playerId, board) +
            number_of_opened_threats_on_columns(threat_length, playerId, board, size) +
            number_of_opened_threats_on_descending_diagonals(threat_length, playerId, board, size) +
            number_of_opened_threats_on_ascending_diagonals(threat_length, playerId, board, size))

# ------------------------- SEMI-OPENED THREATS ------------------------------------


def pattern_(playerId, length, opponentId, pattern_victory_length):
    from itertools import permutations

    data = [playerId for i in range(length)] + ["3"]

    all_permutations = set(permutations(data))

    filtered_permutations = [list(p) for p in all_permutations]

    wall_blocked = [threat for threat in filtered_permutations if threat[0] == playerId and threat[-1] == playerId]
    wall_blocked = ["".join(threat) for threat in wall_blocked] + [playerId * length + "3" * (pattern_victory_length - length), "3" * (pattern_victory_length - length) + playerId * length]

    filtered_permutations_specials = [["3"] + l + ["3"] for l in filtered_permutations if l[0] == playerId and l[-1] == playerId]

    filtered_permutations_two = [["3" * (pattern_victory_length - len(l))] + l + [opponentId] for l in filtered_permutations if l[0] == playerId and l[-1] == playerId]
    filtered_permutations_three = [[opponentId] + l + ["3" * (pattern_victory_length - len(l))] for l in filtered_permutations if l[0] == playerId and l[-1] == playerId]
    #filtered_permutations_four = [[opponentId]+ l + [opponentId] for l in filtered_permutations if l[0] == playerId and l[-1] == playerId and len(l) == pattern_victory_length]

    filtered_permutations = (
            filtered_permutations_two +
            filtered_permutations_three +
            #filtered_permutations_four +
            [[symbol for symbol in opponentId + length * playerId + "3" * (pattern_victory_length - length)]] +
            [[symbol for symbol in "3" * (pattern_victory_length - length) + length * playerId + opponentId]]
    )
    filtered_permutations = ["".join(threat) for threat in filtered_permutations ]
    return filtered_permutations, wall_blocked, [ "".join(threat) for threat in filtered_permutations_specials]



def contains_all_semi_opened_threats(segment, threat_length, playerId, opponentId, pattern_victory_length):
    # Créer les patterns de menaces semi-ouvertes possibles
    patterns, wall_blocked, _ = pattern_(playerId, threat_length, opponentId, pattern_victory_length)

    pattern_find_on_the_left = False
    pattern_find_on_the_right = False

    total_count = 0

    for pattern in patterns:
        start = 0
        while True:
            start = segment.find(pattern, start)
            if start == -1:
                break
            total_count += 1

            # Vérifier si le motif est trouvé au début du segment
            if start == 0:
                pattern_find_on_the_left = True
            # Vérifier si le motif est trouvé à la fin du segment
            if start + len(pattern) == len(segment):
                pattern_find_on_the_right = True

            start += 1  # Avancer pour éviter une boucle infinie

    # Vérification pour wall_blocked si aucun pattern n'a été trouvé aux extrémités
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
    # Créer les patterns de menaces semi-ouvertes possibles
    _, _, dangerous_pattern = pattern_(playerId, threat_length, opponentId, pattern_victory_length)

    total_count = 0

    for pattern in dangerous_pattern:
        start = 0
        while True:
            start = segment.find(pattern, start)
            if start == -1:
                break
            total_count += 1
            start += 1

    return total_count



def number_of_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length):
    count = 0
    for row in board:
        row_str = "".join([str(int(elt)) for elt in row])
        count += contains_all_semi_opened_threats(row_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count

def number_of_dangerous_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length):
    count = 0
    for row in board:
        row_str = "".join([str(int(elt)) for elt in row])
        count += contains_dangerous_semi_opened_threats(row_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count

def number_of_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    count = 0
    for column_number in range(size):
        column_str = "".join([str(int(elt[column_number])) for elt in board])
        count += contains_all_semi_opened_threats(column_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count

def number_of_dangerous_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    count = 0
    for column_number in range(size):
        column_str = "".join([str(int(elt[column_number])) for elt in board])
        count += contains_dangerous_semi_opened_threats(column_str, threat_length, playerId, opponentId, pattern_victory_length)
    return count


def number_of_semi_opened_threats_on_descending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    count = 0
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        while i < size and j < size:
            diagonal += str(int(board[i][j]))
            i += 1
            j += 1
        count += contains_all_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

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
    count = 0
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        while i < size and j < size:
            diagonal += str(int(board[i][j]))
            i += 1
            j += 1
        count += contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    for y in range(1, size):
        diagonal = ""
        i, j = 0, y
        while i < size and j < size:
            diagonal += str(int(board[i][j]))
            i += 1
            j += 1
        count += contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    return count

def number_of_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    count = 0
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        count +=  contains_all_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    for y in range(1, size):
        diagonal = ""
        i, j = size - 1, y
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        count += contains_all_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    return count

def number_of_dangerous_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    count = 0
    for x in range(size):
        diagonal = ""
        i, j = x, 0
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        count +=  contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    for y in range(1, size):
        diagonal = ""
        i, j = size - 1, y
        while i >= 0 and j < size:
            diagonal += str(int(board[i][j]))
            i -= 1
            j += 1
        count += contains_dangerous_semi_opened_threats(diagonal, threat_length, playerId, opponentId, pattern_victory_length)

    return count


def number_of_semi_opened_threats(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    return (number_of_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length) +
            number_of_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_semi_opened_threats_on_descending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length)
            )

def number_of_dangerous_semi_opened_threats(threat_length, playerId, opponentId, board, size, pattern_victory_length):
    return (number_of_dangerous_semi_opened_threats_on_rows(threat_length, playerId, opponentId, board, pattern_victory_length) +
            number_of_dangerous_semi_opened_threats_on_columns(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_dangerous_semi_opened_threats_on_descending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length) +
            number_of_dangerous_semi_opened_threats_on_ascending_diagonals(threat_length, playerId, opponentId, board, size, pattern_victory_length)
            )

def threats_without_holes(playerId, board, size, pattern_victory_length):
    count = 0
    for i in range(size):
        count += (win_on_line(i, playerId, board, pattern_victory_length) +
                  win_on_column(i, playerId, board, pattern_victory_length) +
                  win_on_descending_diagonal(size, i, 0, playerId, board, pattern_victory_length) +
                  win_on_ascending_diagonal(size, i, 0, playerId, board, pattern_victory_length)
                  )
        count += win_on_ascending_diagonal(size, size - 1, i, playerId, board, pattern_victory_length) if i > 0 else 0
        count += win_on_descending_diagonal(size,0, i, playerId, board, pattern_victory_length) if i > 0 else 0
    return count



def won_in_next_move(playerId, board, size, pattern_victory_length, move):
    line, column = divmod(move, size)
    board[line][column] = playerId
    if threats_without_holes(playerId, board, size, pattern_victory_length) > 0:
        return move
    return None

def is_winning_move(playerId, board, size, pattern_victory_length, auhtorized_moves):
    for move in auhtorized_moves:
        result = won_in_next_move(playerId, board.copy(), size, pattern_victory_length, move)
        if result != None:
            return result
    return None







    # -------------------------------------- HEURISTIC -----------------------------------------
def opponent_heuristic_points_calcul(opponentId, playerId, board, size, length_victory_pattern):

    score = 0

    score += (
            0.05 * number_of_semi_opened_threats(length_victory_pattern - 2, opponentId, playerId,  board, size, length_victory_pattern) +
            0.1 * number_of_dangerous_semi_opened_threats(length_victory_pattern - 2, opponentId, playerId,  board, size, length_victory_pattern) +
            1.2 * number_of_opened_threats(length_victory_pattern - 2, opponentId, board, size)

    )

    return score


def agent_heuristic_points_calcul(playerId, opponentId, board, size, length_victory_pattern):

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




def heuristic_points(playerId, opponentId, board, size, length_victory_pattern, auhtorized_moves):
    if is_winning_move(opponentId, board, size, length_victory_pattern, auhtorized_moves) is not None:
        return -5 # 5 before

    bonus = 0
    if is_winning_move(playerId, board, size, length_victory_pattern, auhtorized_moves):
        bonus = 0.1



def estimate_heuristic_bounds(board_size, length_victory_pattern):
    """
    Estime les bornes min/max des valeurs heuristiques en fonction de la taille du plateau
    et des pondérations des menaces.

    board_size : taille du plateau (ex : 3 pour un morpion classique)
    pattern_length : longueur du motif gagnant
    threat_coefficients : liste des pondérations des différentes menaces

    Retourne : (borne_min, borne_max)
    """


    # facteur = 50000 * board_size  * int(board_size / length_victory_pattern)

    max_heuristic = 10000
    min_heuristic = 0

    return min_heuristic, max_heuristic


def normalize(value, board_size, length_victory_pattern):
    min_val, max_val = estimate_heuristic_bounds(board_size, length_victory_pattern)
    return ((value - min_val) / (max_val - min_val))



























