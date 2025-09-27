import pandas
import numpy
import copy
import json

ROWS = 15
COLS = 15
LETTERS_ROW = 16 # where letters are stored on spreadsheet
LETTERS_COL = 0
LETTER_COUNT = 7
BLANK_TILE = '%'
CENTER_COORDS = (7, 7)

gameboard = []
letters = []
valid_entries = []

def main():

    # load word list into memory
    words = set()
    with open("wrds.txt", "r") as inFile:
        for line in inFile:
            words.add(line.strip())
    
    # load gameboard, letters into memory
    sheet = pandas.read_excel("Gameboard.xlsx", header=None).replace(numpy.nan, None)
    for row in range(ROWS):
        newRow = []
        for col in range(COLS):
            newRow.append(sheet.iloc[row, col])
        gameboard.append(newRow)
    for n in range(LETTER_COUNT):
        letters.append(sheet.iloc[16, LETTERS_COL + n])

    # check if this is the beginning of the game
    beggining_of_game = True
    for row in gameboard:
        for tile in row:
            if not tile == None:
                beggining_of_game = False

# ------------------------------------------------------------------------------------------------------------

    # start algorithm
    mainCounter = 0
    for row in range(ROWS):
        for col in range(COLS):
            for word in words:

                valid_across = True
                valid_down = True

                # too long
                if col + len(word) >= COLS:
                    valid_across = False
                if row + len(word) >= ROWS:
                    valid_down = False

                # must pass through center if we are just starting the game
                if beggining_of_game:
                    if ( (col + len(word) - 1 < CENTER_COORDS[0]) or (col > CENTER_COORDS[0]) ) or (not row == CENTER_COORDS[0]):
                        valid_across = False
                    if ( (row + len(word) - 1 < CENTER_COORDS[1]) or (row > CENTER_COORDS[1]) ) or (not col == CENTER_COORDS[1]):
                        valid_down = False

# ------------------------------------------------------------------------------------------------------------

                # interferes with other letters OR you didnt play any letters
                letter_on_board_indexes_ACROSS = []
                if valid_across and not beggining_of_game:
                    for index, letter in enumerate(word):
                        if (gameboard[row][col + index] == letter):
                            letter_on_board_indexes_ACROSS.append(index)
                        if (not gameboard[row][col + index] == None) and (not gameboard[row][col + index] == letter):
                            valid_across = False
                if len(word) == len(letter_on_board_indexes_ACROSS):
                    valid_across = False

                letter_on_board_indexes_DOWN = []
                if valid_down and not beggining_of_game:
                    for index, letter in enumerate(word):
                        if (gameboard[row + index][col] == letter):
                            letter_on_board_indexes_DOWN.append(index)
                        if (not gameboard[row + index][col] == None) and (not gameboard[row + index][col] == letter):
                            valid_down = False
                if len(word) == len(letter_on_board_indexes_DOWN):
                    valid_down = False


# ------------------------------------------------------------------------------------------------------------
                            
                # you can't write this word with your letters
                if valid_across:
                    letters_cpy = list(letters)
                    for index, letter in enumerate(word):
                        if (index not in letter_on_board_indexes_ACROSS):
                            if (letter in letters_cpy):
                                letters_cpy.remove(letter)
                            elif BLANK_TILE in letters_cpy:
                                letters_cpy.remove(BLANK_TILE)
                            else:
                                valid_across = False
                                break
                if valid_down:
                    letters_cpy = list(letters)
                    for index, letter in enumerate(word):
                        if (index not in letter_on_board_indexes_DOWN):
                            if (letter in letters_cpy):
                                letters_cpy.remove(letter)
                            elif BLANK_TILE in letters_cpy:
                                letters_cpy.remove(BLANK_TILE)
                            else:
                                valid_down = False
                                break

# ------------------------------------------------------------------------------------------------------------

                # word is not connected to other game tiles (does not matter on the first turn) ##RETHINK!!!!
                if not beggining_of_game:
                    if valid_across:
                        isolated_position = True
                        if (col - 1) >= 0 and (not gameboard[row][col - 1] == None):
                            isolated_position = False
                        if (col + len(word)) < COLS and (not gameboard[row][col + len(word)] == None):
                            isolated_position = False
                        for column in range(col, col + len(word)):
                            if (row - 1) >= 0 and (not gameboard[row - 1][column] == None):
                                isolated_position = False
                                break
                            if (not gameboard[row][column] == None):
                                isolated_position = False
                                break
                            if (row + 1) < ROWS and (not gameboard[row + 1][column] == None):
                                isolated_position = False
                                break
                        if isolated_position:
                            valid_across = False

                    if valid_down:
                        isolated_position = True
                        if (row - 1) >= 0 and (not gameboard[row - 1][col] == None):
                            isolated_position = False
                        if (row +len(word)) < ROWS and (not gameboard[row + len(word)][col] == None):
                            isolated_position = False
                        for rownum in range(row, row + len(word)):
                            if (col - 1) >= 0 and (not gameboard[rownum][col - 1] == None):
                                isolated_position = False
                                break
                            if (not gameboard[rownum][col] == None):
                                isolated_position = False
                                break
                            if (col + 1) < COLS and (not gameboard[rownum][col + 1] == None):
                                isolated_position = False
                                break
                        if isolated_position:
                            valid_down = False

# ------------------------------------------------------------------------------------------------------------


                # words that are created by contact are not valid words (does not matter on the first turn)
                if valid_across:
                    gameboard_cpy = copy.deepcopy(gameboard)
                    string_list_ACROSS = []
                    for index, letter in enumerate(word):
                        gameboard_cpy[row][col + index] = letter
                        char_list = []
                        # new strings vertical
                        if index not in letter_on_board_indexes_ACROSS:
                            char_list.append(letter)
                            for n in range(1, row + 1):
                                cell_above = gameboard_cpy[row - n][col + index]
                                if not cell_above == None:
                                    char_list.insert(0, cell_above)
                                else:
                                    break
                            for n in range(1, ROWS - row):
                                cell_below = gameboard_cpy[row + n][col + index]
                                if not cell_below == None:
                                    char_list.append(cell_below)
                                else:
                                    break
                            if len(char_list) > 1:
                                string_list_ACROSS.append( {"word": ''.join(char_list), "your letters": [ {"letter": letter, "coords": (row, col + index)} ] } )
                    # new string horizontal
                    char_list = [gameboard_cpy[row][col]]
                    for n in range(1, col + 1):
                        cell_left = gameboard_cpy[row][col - n]
                        if not cell_left == None:
                            char_list.insert(0, cell_left)
                        else:
                            break
                    for n in range(1, COLS - col):
                        cell_right = gameboard_cpy[row][col + n]
                        if not cell_right == None:
                            char_list.append(cell_right)
                        else:
                            break

                    # find positions of YOUR letters in this horizontal string
                    your_letter_coords = []
                    for index, letter in enumerate(word):
                        if index not in letter_on_board_indexes_ACROSS:
                            your_letter_coords.append( { "letter": letter, "coords": (row, col + index) } )
                    string_list_ACROSS.append({"word": ''.join(char_list), "your letters": your_letter_coords})

                    # check if these strings are valid
                    for datum in string_list_ACROSS:
                        if datum["word"] not in words:
                            valid_across = False

# ------------------------------------------------------------------------------------------------------------

                if valid_down:
                    gameboard_cpy = copy.deepcopy(gameboard)
                    string_list_DOWN = []
                    for index, letter in enumerate(word):
                        gameboard_cpy[row + index][col] = letter
                        char_list = []
                        # new strings horizontal
                        if index not in letter_on_board_indexes_DOWN:
                            char_list.append(letter)
                            for n in range(1, col + 1):
                                cell_left = gameboard_cpy[row + index][col - n]
                                if not cell_left == None:
                                    char_list.insert(0, cell_left)
                                else:
                                    break
                            for n in range(1, COLS - col):
                                cell_right = gameboard_cpy[row + index][col + n]
                                if not cell_right == None:
                                    char_list.append(cell_right)
                                else:
                                    break
                            if len(char_list) > 1:
                                string_list_DOWN.append( {"word": ''.join(char_list), "your letters": [ {"letter": letter, "coords": (row + index, col)} ] } )
                    # new string vertical
                    char_list = [gameboard_cpy[row][col]]
                    for n in range(1, row + 1):
                        cell_above = gameboard_cpy[row - n][col]
                        if not cell_above == None:
                            char_list.insert(0, cell_above)
                        else:
                            break
                    for n in range(1, ROWS - row):
                        cell_below = gameboard_cpy[row + n][col]
                        if not cell_below == None:
                            char_list.append(cell_below)
                        else:
                            break

                    # find positions of YOUR letters in this vertical string
                    your_letter_coords = []
                    for index, letter in enumerate(word):
                        if index not in letter_on_board_indexes_DOWN:
                            your_letter_coords.append( { "letter": letter, "coords": (row + index, col) } )
                    string_list_DOWN.append({"word": ''.join(char_list), "your letters": your_letter_coords})

                    # check if these strings are valid
                    for datum in string_list_DOWN:
                        if datum["word"] not in words:
                            valid_down = False

# ------------------------------------------------------------------------------------------------------------

                if valid_across:
                    points_across = tally_points(string_list_ACROSS)
                if valid_down:
                    points_down = tally_points(string_list_DOWN)

                # if the word is valid, store it as a valid entry
                if valid_across:
                    new_entry = {
                        "Word": word,
                        "Position": (row, col),
                        "Config": "ACROSS",
                        "Points": points_across
                    }
                    valid_entries.append(new_entry)

                if valid_down:
                    new_entry = {
                        "Word": word,
                        "Position": (row, col),
                        "Config": "DOWN",
                        "Points": points_down
                    }
                    valid_entries.append(new_entry)

            mainCounter += 1
            print(f"Progress: {(( mainCounter / (ROWS * COLS) ) * 100):.2f}%")

    # python builtin sorting algorithm
    sorted_valid_entries = sorted(valid_entries, key=lambda x: x["Points"], reverse=True)
    with open("output.txt", "w", encoding="utf-8") as f:
        for entry in sorted_valid_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------------------------

TW_coords = [ (0, 3), (0, 11), (3, 0), (3, 14), (11, 0), (11, 14), (14, 3), (14, 11) ]
DW_coords = [ (1, 5), (1, 9), (3, 7), (5, 1), (5, 13), (7, 3), (7, 7), (7, 11), (9, 1), (9, 13), (11, 7), (13, 5), (13, 9) ]
TL_coords = [ (0, 6), (0, 8), (3, 3), (3, 11), (5, 5), (5, 9), (6, 0), (6, 14), (8, 0), (8, 14), (9, 5), (9, 9), (11, 3), (11, 11), (14, 6), (14, 8) ]
DL_coords = [ (1, 2), (1, 12), (2, 1), (2, 4), (2, 10), (2, 13), (4, 2), (4, 6), (4, 8), (4, 12), (6, 4), (6, 10), (8, 4), (8, 10), (10, 2), (10, 6), 
              (10, 8), (10 ,12), (12, 1), (12, 4), (12, 10), (12, 13), (13, 2), (13, 12) ]

Letter_point_values = { BLANK_TILE: 0, 'a': 1, 'b': 4, 'c': 4, 'd': 2, 'e': 1, 'f': 4, 'g': 3, 'h': 3, 
                                       'i': 1, 'j': 10, 'k': 5, 'l': 2, 'm': 4, 'n': 2, 'o': 1, 'p': 4,
                                       'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 2, 'v': 5, 'w': 4, 'x': 8,
                                       'y': 3, 'z': 10 }

def tally_points(string_list):
    totalPointSum = 0
    all_tiles = False
    for dictionary in string_list:
        pointSum = 0
        TW_counter = 0
        DW_counter = 0
        char_list = list(dictionary["word"])
        if len(dictionary["your letters"]) == LETTER_COUNT:
            totalPointSum += 35
        for datum in dictionary["your letters"]:
            if datum["coords"] in TL_coords:
                pointSum += 3 * Letter_point_values[datum["letter"]]
            elif datum["coords"] in DL_coords:
                pointSum += 2 * Letter_point_values[datum["letter"]]
            else:
                pointSum += Letter_point_values[datum["letter"]]
            if datum["coords"] in TW_coords:
                TW_counter += 1
            elif datum["coords"] in DW_coords:
                DW_counter += 1
            char_list.remove(datum["letter"])
        for letter in char_list:
            pointSum += Letter_point_values[letter]
        pointSum *= (3 ** TW_counter)
        pointSum *= (2 ** DW_counter)
        totalPointSum += pointSum
    if all_tiles:
        totalPointSum == 35
    return totalPointSum

main()
