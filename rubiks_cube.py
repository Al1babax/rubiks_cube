from idlelib.debugobj import make_objecttreeitem
from typing import List
from random import choice
from color import Colors
from solver import Solver


class Test:
    def __init__(self, cube):
        self.cube = cube

    def find_duplicate_move(self):
        # Run moves to find if any move results in duplicate squares, 1000 tries
        # There should always be 9 of each color
        # Returns false if fail and true if succeed

        for test_ran in range(1000):
            self.cube.init_cube()
            self.cube.random_shuffle(1)
            temp_memory = {}
            for row in self.cube.cube[:9]:
                for col in row:
                    if col == "":
                        if "-" in temp_memory.keys():
                            temp_memory["-"] += 1
                        else:
                            temp_memory["-"] = 1
                    else:
                        letter = col[0]

                        if letter in temp_memory.keys():
                            temp_memory[letter] += 1
                        else:
                            temp_memory[letter] = 1

            # Check if memory is correct
            for key, value in temp_memory.items():
                if key.isalpha() and value != 9:
                    print(f"{key} did not have 9 items --> had {value} items")
                    print(self.cube.show())
                    return False
                elif key == "" and value != 54:
                    print(f"Not the right amount of empty squares, had {value}")
                    print(self.cube.show())
                    return False

            print(f"Test {test_ran + 1} ran successfully")

        return True


class Cube:
    def __init__(self, size, debug=False, text=True):
        self.colors = ["O", "G", "W", "B", "Y", "R"]
        self.all_sides = ["top", "left", "front", "right", "back", "bottom", "back"]
        self.sides_dict = {
            "top": (0, 1),
            "left": (1, 0),
            "front": (1, 1),
            "right": (1, 2),
            "back1": (1, 3),
            "bottom": (2, 1),
            "back2": (3, 1)
        }

        # SIZE HAS TO BE 3, not all function work with other sizes
        self.size = size
        self.cube = []

        # Last time each backside was updated, used for syncing (0 = no sync needed, 1 = back2 needs sync, 2 = back1 needs sync)
        self.back_updates = 0

        # DEBUG mode
        self.DEBUG = debug

        # Init
        self.init_cube()

        # Init color class
        self.colorer = Colors()

        self.show_text = text

        self.solver = Solver(self)

    def create_side(self, side_color=None):
        temp_side = []
        if side_color not in self.colors:
            for _ in range(self.size):
                temp_side.append([""] * self.size)

        elif side_color and self.DEBUG:
            for i in range(self.size):
                temp_line = []
                for j in range(self.size):
                    temp_line.append(f"{side_color}{i * 3 + j + 1}")
                temp_side.append(temp_line)
        else:
            for i in range(self.size):
                temp_side.append([side_color] * 3)

        return temp_side

    def init_cube(self):
        # Reset the cube first
        self.cube = []

        # Add all the colors
        for color in self.colors:
            self.cube.append(self.create_side(color))

        self.cube.append(self.create_side("Y"))

        # Add empty sides
        index_pos = [0, 2, 2, 8, 10, 10, 10, 14, 14]

        for index in index_pos:
            self.cube.insert(index, self.create_side())

        # Convert into 2d
        def side_batch_generator():
            # Take 4 sides per time and yield
            for i in range(4):
                yield self.cube[(i * 4):(i * 4) + 4]

        batch_gen = side_batch_generator()

        new_cube = []

        # Loop over the batches
        for batch in batch_gen:
            # Loop over the 3 rows in one batch
            for row in range(3):
                new_row = []
                # Loop over each side in the batch
                for side in range(4):
                    # Loop over each character on each side on each line
                    for char in batch[side][row]:
                        new_row.append(char)

                new_cube.append(new_row)

        self.cube = new_cube

        # Sync the back2
        self.back_updates = 1

        self.sync_back()

    def show(self):
        for row in self.cube:
            for char in row:
                if char == "" and self.show_text:
                    print(" -  ", end="")
                elif char == "":
                    print("   ", end="")
                else:
                    text = f" {char} " if self.show_text else f"   "
                    print(f"{self.colorer.color_text(text, self.colorer.square_to_color[char[0]])}", end="")

            print("\n", end="")

        print("\n")

    def get_side(self, side: str) -> List:
        temp_side = []

        for row in self.cube[self.sides_dict[side][0] * 3:self.sides_dict[side][0] * 3 + 3]:
            temp_side.append(row[self.sides_dict[side][1] * 3:self.sides_dict[side][1] * 3 + 3])

        return temp_side

    def set_side(self, side: str, new_side: List[List]) -> None:
        side_row, side_col = self.sides_dict[side]

        for row in range(3):
            for col in range(3):
                self.cube[side_row * 3 + row][side_col * 3 + col] = new_side[row][col]

    def sync_back(self) -> None:
        # Check which backside is older and sync that to the newer one
        # Also have to sync in reverse col and rows aka mirroring

        # no need to update
        if self.back_updates == 0:
            return

        # Check which needs back needs syncing
        side_to_update = "back1" if self.back_updates == 2 else "back2"
        real_side = "back1" if side_to_update == "back2" else "back2"

        # Get the real back
        updated_side = self.get_side(real_side)

        # Mirror
        new_side = [line[::-1] for line in updated_side[::-1]]

        # Update the old back
        self.set_side(side_to_update, new_side)

        self.back_updates = 0

    def slide_long(self, direction: str, row=None, col=None) -> None:
        """
        Slide either horizontally or vertically a line (3,4,5)
        :param direction: up, down, left, right
        :param row: row to be rotated
        :param col: col to be rotated
        :return:
        """
        if direction == "right":
            temp = self.cube[row][-3:]
            self.cube[row] = temp + self.cube[row][:-3]
            if row == 3:
                self.rotate_side("top", "counter-clockwise")
            elif row == 5:
                self.rotate_side("bottom", "clockwise")
        elif direction == "left":
            temp = self.cube[row][:3]
            self.cube[row] = self.cube[row][3:] + temp
            if row == 3:
                self.rotate_side("top", "clockwise")
            elif row == 5:
                self.rotate_side("bottom", "counter-clockwise")
        elif direction == "up":
            temp = [x[col] for x in self.cube[0:3]]

            for i in range(12):
                if i < 9:
                    self.cube[i][col] = self.cube[i + 3][col]
                else:
                    self.cube[i][col] = temp[i - 9]

            if col == 3:
                self.rotate_side("left", "counter-clockwise")
            elif col == 5:
                self.rotate_side("right", "clockwise")
        elif direction == "down":
            temp = [x[col] for x in self.cube[-3:]]

            for i in range(12):
                if i < 9:
                    self.cube[11 - i][col] = self.cube[11 - i - 3][col]
                else:
                    self.cube[11 - i][col] = temp[11 - i]

            if col == 3:
                self.rotate_side("left", "clockwise")
            elif col == 5:
                self.rotate_side("right", "counter-clockwise")

        # Manage back sync
        if direction in ["up", "down"]:
            self.back_updates = 2
        elif direction in ["left", "right"]:
            self.back_updates = 1

        self.sync_back()

    def rotate_side(self, side: str, direction: str) -> None:
        """
        Side to be rotated, front, back1 or back2 NOT supported
        :param direction: clockwise or counter-clockwise
        :param side: side
        :return:
        """
        temp_side = self.get_side(side)

        new_side = []

        for col in range(3):
            temp_line = []
            for row in range(3):
                if direction == "clockwise":
                    temp_line.append(temp_side[2 - row][col])
                elif direction == "counter-clockwise":
                    temp_line.append(temp_side[row][2 - col])

            new_side.append(temp_line)

        self.set_side(side, new_side)

    def rotate_big(self, side: str) -> None:
        # Rotates either the front or back1
        if side in ["back1", "back2"]:
            self.change_perspective("right")
            self.change_perspective("right")

        self.change_perspective("right")
        self.slide_long("up", 5, 5)
        self.change_perspective("left")

        if side in ["back1", "back2"]:
            self.change_perspective("right")
            self.change_perspective("right")

    def change_perspective(self, direction: str):
        """
        Changes the direction of perspective
        :param direction: up, left, right, down
        :return:
        """
        match direction:
            case "up":
                for i in range(3):
                    self.slide_long("up", row=0, col=3 + i)

            case "down":
                for i in range(3):
                    self.slide_long("down", row=0, col=3 + i)

            case "left":
                for i in range(3):
                    self.slide_long("left", row=3 + i, col=0)

            case "right":
                for i in range(3):
                    self.slide_long("right", row=3 + i, col=0)

    def rotate_whole(self) -> None:
        # Rotate whole cube clockwise from front
        for side in self.sides_dict.keys():
            if side == "back2":
                continue
            elif side == "back1":
                self.rotate_side(side, "counter-clockwise")
            else:
                self.rotate_side(side, "clockwise")

        # Sync back
        self.back_updates = 1
        self.sync_back()

        temp_top = self.get_side("top")
        self.set_side("top", self.get_side("left"))
        self.set_side("left", self.get_side("bottom"))
        self.set_side("bottom", self.get_side("right"))
        self.set_side("right", temp_top)

    def random_shuffle(self, amount: int = 1000, output=False) -> None:
        # Do random moves to shuffle the cube
        directions = ["up", "down", "left", "right"]
        numbers = [3, 4, 5]

        actions = ["rotate", "slide", "p_change"]

        for _ in range(amount):
            random_action = choice(actions)

            match random_action:
                case "rotate":
                    for _ in range(choice([1, 2, 3])):
                        self.rotate_big("front")
                case "slide":
                    random_direction = choice(directions)
                    random_number = choice(numbers)
                    self.slide_long(random_direction, random_number, random_number)
                case "p_change":
                    random_direction = choice(directions)
                    self.change_perspective(random_direction)

    def controls(self):
        direction_shorts = {
            "u": "up",
            "d": "down",
            "l": "left",
            "r": "right"
        }

        # Controls for the cube for the user
        while True:
            self.show()

            user_input = input(
                "Select select row/col and u/d/l/r (up/down/left/right)(q to quit) or change perspective u/d/l/r or rotate front f or ra = righty algo, la = lefty algo, wr = whole rotate, wc = white cross, sl = second layer: ")

            if user_input == "sl":
                self.solver.second_layer()
                continue

            if user_input == "wc":
                self.solver.solve()
                continue

            if user_input == "q":
                break

            if len(user_input) == 2 and user_input == "wr":
                self.rotate_whole()
                continue

            if len(user_input) == 2 and user_input == "ra":
                self.slide_long("up", 5, 5)
                self.slide_long("left", 3, 3)
                self.slide_long("down", 5, 5)
                self.slide_long("right", 3, 3)
                continue

            if len(user_input) == 2 and user_input == "la":
                self.slide_long("up", 3, 3)
                self.slide_long("right", 3, 3)
                self.slide_long("down", 3, 3)
                self.slide_long("left", 3, 3)
                continue

            if len(user_input) == 1 and user_input[0] in ["u", "d", "l", "r"]:
                self.change_perspective(direction_shorts[user_input[0]])
                continue

            if len(user_input) == 1 and user_input == "f":
                self.rotate_big("front")
                continue

            if len(user_input) != 2 or user_input[0] not in "345" or user_input[1] not in ["u", "d", "l", "r"]:
                print(f"Invalid input")
                continue

            rc = int(user_input[0])
            direction = direction_shorts[user_input[1]]
            self.slide_long(direction, rc, rc)


def sync_test():
    rubiks_cube = Cube(3, debug=True)

    rubiks_cube.show()

    new_back = [["B", "B", "B"], ["Y", "Y", "Y"], ["Y", "Y", "Y"]]

    rubiks_cube.set_side("back1", new_back)
    rubiks_cube.back_updates = 1
    rubiks_cube.sync_back()

    rubiks_cube.show()


def generate_random_moves(amount):
    moves1 = []
    moves2 = []

    numbers = [3, 4, 5]
    directions = ["up", "left", "right", "down"]

    for _ in range(amount):
        roc = choice(numbers)
        direction = choice(directions)
        moves1.append((roc, direction))
        moves2.append((roc - 3, direction))

    return moves1, moves2


def execute_moves(cube: Cube, moves: List, output=True):
    for num, move in enumerate(moves):
        if output:
            print(f"Move number {num + 1}, move {move}")

        cube.slide_long(move[1], move[0], move[0])

        if output:
            cube.show()
            print()

    return cube


def test_daisy():
    for _ in range(100):
        rubiks_cube = Cube(3, debug=True)
        rubiks_cube.random_shuffle(100)
        solver = Solver(rubiks_cube)
        solver.daisy()


def main():
    rubiks_cube = Cube(3, debug=True)
    # rubiks_cube.cube = [['', '', '', 'G7', 'W6', 'Y7', '', '', '', '', '', ''], ['', '', '', 'Y2', 'W5', 'W2', '', '', '', '', '', ''], ['', '', '', 'B1', 'W8', 'G3', '', '', '', '', '', ''], ['R7', 'O2', 'O9', 'W3', 'R2', 'W1', 'O7', 'O8', 'B9', 'R9', 'B4', 'Y9'], ['R8', 'R5', 'G4', 'Y6', 'B5', 'B2', 'O6', 'O5', 'O4', 'G2', 'G5', 'Y8'], ['B7', 'G6', 'G1', 'Y3', 'R6', 'B3', 'O3', 'B6', 'W7', 'R1', 'R4', 'W9'], ['', '', '', 'O1', 'B8', 'Y1', '', '', '', '', '', ''], ['', '', '', 'W4', 'Y5', 'Y4', '', '', '', '', '', ''], ['', '', '', 'R3', 'G8', 'G9', '', '', '', '', '', ''], ['', '', '', 'W9', 'R4', 'R1', '', '', '', '', '', ''], ['', '', '', 'Y8', 'G5', 'G2', '', '', '', '', '', ''], ['', '', '', 'Y9', 'B4', 'R9', '', '', '', '', '', '']]
    # rubiks_cube.random_shuffle(1000)
    print(rubiks_cube.cube)
    # rubiks_cube.show()
    # print(rubiks_cube.cube)
    solver = Solver(rubiks_cube)
    solver.solve()
    # print(rubiks_cube.cube)
    rubiks_cube.controls()



if __name__ == '__main__':
    # test_daisy()
    main()
