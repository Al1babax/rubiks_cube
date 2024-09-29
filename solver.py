from typing import List


class Solver:
    def __init__(self, cube):
        self.cube = cube
        self.white_targets = ["W2", "W4", "W6", "W8"]
        self.rotation_dir = {
            "left": 270,
            "top": 180,
            "right": 90,
            "bottom": 0
        }

    def left_algorithm(self):
        self.cube.slide_long("up", 3, 3)
        self.cube.slide_long("right", 3, 3)
        self.cube.slide_long("down", 3, 3)
        self.cube.slide_long("left", 3, 3)

    def right_algorithm(self):
        self.cube.slide_long("up", 5, 5)
        self.cube.slide_long("left", 3, 3)
        self.cube.slide_long("down", 5, 5)
        self.cube.slide_long("right", 3, 3)

    def change_center(self, target):
        # Loop through all the sides of the cube and find the Y5, when found change perspective to that side
        directions = {
            "top": ["up"],
            "right": ["right"],
            "left": ["left"],
            "bottom": ["down"],
            "back1": ["right", "right"],
            "back2": ["right", "right"]
        }

        # Check if already in center
        if self.cube.get_side("front")[1][1] == target:
            return

        for side, pos in self.cube.sides_dict.items():
            for row in self.cube.get_side(side):
                if target in row:
                    commands = directions[side]

                    for command in commands:
                        self.cube.change_perspective(command)

    def roll_freebies(self):
        freebies_found = 0

        # Loop through rows,cols 3 and 5 and move white sides to front face if the line is "free"
        lines = [3, 5]

        # Check horizontal
        self.white_targets = ["W2", "W4", "W6", "W8"]
        for row in lines:
            items_found = []

            # Look for all the targets
            for col, cell in enumerate(self.cube.cube[row]):
                if cell in self.white_targets:
                    items_found.append(cell)

            # if only one target is found, shift that line to right until the target is in front side
            if len(items_found) == 0:
                continue
            elif self.cube.cube[row][4] in self.white_targets:
                continue

            # rotate that line until the target is in front
            while self.cube.cube[row][4] != items_found[0]:
                freebies_found = 1
                self.cube.slide_long("right", row, row)

        # Check vertical
        for col in lines:
            items_found = []

            for row in range(12):
                if self.cube.cube[row][col] in self.white_targets:
                    items_found.append(self.cube.cube[row][col])

            if len(items_found) == 0:
                continue
            elif self.cube.cube[4][col] in self.white_targets:
                continue

            while self.cube.cube[4][col] != items_found[0]:
                freebies_found = 1
                self.cube.slide_long("down", col, col)

        return False if freebies_found == 0 else True

    def find_new_freebie(self):
        def find_last_target():
            # Find the last missing target
            targets = ["W2", "W4", "W6", "W8"]

            for side in self.cube.sides_dict.keys():
                if side == "front":
                    continue

                for row in self.cube.get_side(side):
                    for cell in row:
                        if cell in targets:
                            return [cell, side]

        # Find how to make the last white a freebie
        last_target = find_last_target()

        if last_target is None:
            return

        # If target was found on back1, then temporarily shift perspective to left and back right at the end
        perspective_changed = 0

        if last_target[1] in ["back1", "back2"]:
            self.cube.change_perspective("left")
            last_target[1] = "right"
            perspective_changed = 1

        # First rotate the center to point at missing target
        relative_position = self.cube.sides_dict[last_target[1]]
        while self.cube.get_side("front")[relative_position[0]][relative_position[1]] in self.white_targets:
            self.cube.rotate_big("front")

        # Move last target to row, col 3, depending on which side it was found
        # if missing on left, 3up | right, 5up | top, 3right | bottom, 5right |
        command_dict = {
            "top": (3, "right"),
            "left": (3, "up"),
            "bottom": (5, "right"),
            "right": (5, "up")
        }
        dir_dict = {
            "top": (1, 2),
            "left": (0, 1),
            "bottom": (1, 0),
            "right": (2, 1)
        }
        position_to_look = dir_dict[last_target[1]]

        if last_target[1] in ["top", "bottom"]:
            while self.cube.get_side(last_target[1])[position_to_look[0]][position_to_look[1]] != last_target[0]:
                move = command_dict[last_target[1]]
                self.cube.slide_long(move[1], move[0], move[0])
        elif last_target[1] in ["right", "left"]:
            while self.cube.get_side(last_target[1])[position_to_look[0]][position_to_look[1]] != last_target[0]:
                move = command_dict[last_target[1]]
                self.cube.slide_long(move[1], move[0], move[0])

        if perspective_changed == 1:
            self.cube.change_perspective("right")

        # Rotate front so that the last target is on freebie line
        self.cube.rotate_big("front")

        # roll freebies
        self.roll_freebies()

    def find_targets(self, side: List[List], targets) -> int:
        found = 0
        for row in side:
            for cell in row:
                if cell in targets:
                    found += 1

        return found

    def daisy(self):
        # Make daisy with yellow center and whites on the side
        try:
            self.move_to_front("Y5")
        except:
            self.cube.show()
            raise ("Was not able to change center")

        # Find all freebies
        try:
            while self.roll_freebies():
                pass
        except:
            self.cube.show()
            raise ("Was not able to find freebies")

        # Run this until all 4 pedals in right place
        try:
            while self.find_targets(self.cube.get_side("front"), self.white_targets) < 4:
                self.find_new_freebie()
        except:
            self.cube.show()
            raise ("Was not able to get all 4 pedals right")

    def white_cross(self):
        # Make correct white cross
        side_dir = {
            "top": [(3, "right"), (2, 4), (1, 4), (3, 4)],
            "left": [(3, "down"), (4, 2), (4, 1), (4, 3)],
            "right": [(5, "down"), (4, 6), (4, 7), (4, 5)],
            "bottom": [(5, "right"), (6, 4), (7, 4), (5, 4)],
        }
        targets_moved = 0

        while targets_moved < 4:
            # Search for white target in front

            # Check if any side is aligned
            for key, values in side_dir.items():
                row, col = values[3]

                # Check that side has target
                if self.cube.cube[row][col] not in self.white_targets:
                    continue

                sq1_r, sq1_c = values[1]
                sq2_r, sq2_c = values[2]

                # Check if side is aligned
                if self.cube.cube[sq1_r][sq1_c][0] != self.cube.cube[sq2_r][sq2_c][0]:
                    continue

                # Move the target
                self.cube.slide_long(values[0][1], values[0][0], values[0][0])
                self.cube.slide_long(values[0][1], values[0][0], values[0][0])

                targets_moved += 1

            self.cube.rotate_big("front")

        self.cube.change_perspective("left")
        self.cube.change_perspective("left")

    def find_target_pos(self, matrix, target):
        # Find the targets from matrix using first character of the square
        target_positions = []
        for row in range(len(matrix)):
            for col in range(len(matrix[0])):
                if matrix[row][col] == "":
                    continue

                if matrix[row][col][0] == target:
                    target_positions.append([row + 2, col + 2])

        return target_positions

    def rotate_matrix(self, matrix: List[List]) -> List[List]:
        while matrix[1][0] != "":
            matrix = [list(row) for row in zip(*matrix[::-1])]

        return matrix

    def find_relative_position(self, matrix):
        # First rotate the matrix so that empty square is on bottom left
        rotated_matrix = self.rotate_matrix(matrix)

        if rotated_matrix[0][1][0] == "W":
            return "up"
        elif rotated_matrix[1][1][0] == "W":
            return "right"
        elif rotated_matrix[0][0][0] == "W":
            return "left"

    def get_neighbours(self, target_pos):
        # Gets the other sides of the corner piece, coordinates and colors and the position of white
        neighbor_dir = {
            "top_left": (2, 2),
            "top_right": (2, 5),
            "bottom_left": (5, 2),
            "bottom_right": (5, 5)
        }

        target_pos = [target_pos[0] - 2, target_pos[1] - 2]

        # Find side
        if target_pos[0] < 3:
            side = "top_left" if target_pos[1] < 3 else "top_right"
        else:
            side = "bottom_left" if target_pos[1] < 3 else "bottom_right"

        side_pos = neighbor_dir[side]
        area = [row[side_pos[1]:side_pos[1] + 2] for row in self.cube.cube[side_pos[0]:side_pos[0] + 2]]

        # Get neighbours
        neighbours = []

        for row in range(len(area)):
            for col in range(len(area[0])):
                cell = area[row][col]
                if cell == "":
                    continue
                elif cell[0] != "W":
                    neighbours.append(cell)

        # Based on empty pos get white side on the small cube
        side = self.find_relative_position(area)

        return neighbours, side

    def is_white_done(self):
        for row in self.cube.get_side("back1"):
            for cell in row:
                if cell[0] != "W":
                    return False

        return True

    def is_aligned(self, neighbours, corner_pos) -> bool:
        # Check if the corner piece neighbour colors are aligning with side centers
        sides = corner_pos.split("_")

        for side in sides:
            side_center = self.cube.get_side(side)[1][1]

            if side_center[0] != neighbours[0][0] and side_center[0] != neighbours[1][0]:
                return False

        return True

    def move_to_front(self, center):
        # Move right 4 times
        for _ in range(4):
            if self.cube.cube[4][4] == center:
                return

            self.cube.change_perspective("right")

        # Move up 4 times
        for _ in range(4):
            if self.cube.cube[4][4] == center:
                return

            self.cube.change_perspective("up")

    def change_side_and_rotate(self, side, rotation):
        """
        Change the side to be front, and rotate with given degrees
        :param side: front, right, left, bottom, back
        :param rotation: 90, 180, 270
        :return:
        """
        top_side_symbol = self.cube.get_side(side)[1][1]
        self.move_to_front(top_side_symbol)

        for _ in range(int(rotation) // 90):
            self.cube.rotate_whole()

    def fix_rogue(self):
        self.move_to_front("W5")
        self.cube.change_perspective("down")

        # Move white to bottom until rogue white on either slide, then if rogue in slide1 do lefty algo and slide2 right
        while True:
            slide1 = [row[2] for row in self.cube.cube[3:6]]
            slide2 = [row[6] for row in self.cube.cube[3:6]]

            for cell in slide1:
                if cell[0] == "W":
                    self.left_algorithm()
                    return

            for cell in slide2:
                if cell[0] == "W":
                    self.right_algorithm()
                    return

            self.cube.rotate_whole()
            self.move_to_front("W5")
            self.cube.change_perspective("down")

    def check_white_corners(self) -> bool:
        def check_corners() -> bool:
            for _ in range(4):
                bottom_face = self.cube.get_side("bottom")
                bottom_center_color = bottom_face[1][1][0]

                for i in range(3):
                    if i == 1:
                        continue

                    if bottom_face[2][i][0] != bottom_center_color:
                        # False white corner
                        self.cube.change_perspective("up")

                        if i == 0:
                            self.left_algorithm()
                        elif i == 2:
                            self.right_algorithm()

                        self.move_to_front("Y5")
                        return False

            return True

        # Returns true if everything ok
        self.move_to_front("Y5")
        if not check_corners():
            return False

        # Have to check the other side too
        self.cube.rotate_whole()
        self.cube.rotate_whole()

        if not check_corners():
            return False

        return True

    def white_corners(self):
        # First make white cross bottom
        self.cube.change_perspective("right")
        self.cube.change_perspective("right")

        while True:
            # Look for white corner piece
            big_area = [row[2:7] for row in self.cube.cube[2:7]]
            targets = self.find_target_pos(big_area, "W")

            # if no targets are found check if white side is done, if not find the rogue square and move it to middle
            if len(targets) == 0:
                if self.is_white_done():
                    # Make sure none of the white pieces were on wrong position in the beginning
                    if self.check_white_corners():
                        # Break if everything ok
                        break
                    else:
                        # Continue if you need fixing
                        continue

                # Perform algo here to move the rogue square
                self.fix_rogue()
                self.change_center("Y5")

                continue

            for target in targets:
                big_area_target_pos = [target[0] - 2, target[1] - 2]
                target_symbol = big_area[big_area_target_pos[0]][big_area_target_pos[1]]

                # Get neighbours
                corner_info = self.get_neighbours(target)

                # Get corner position (top_left, top_right, bottom_left, bottom_right)
                if target[0] <= 3:
                    corner_pos = "top_left" if target[1] < 4 else "top_right"
                else:
                    corner_pos = "bottom_left" if target[1] < 4 else "bottom_right"

                # Check if neighbours are aligned
                if not self.is_aligned(corner_info[0], corner_pos):
                    continue

                # Change the correct side
                # If white is on left or right, get both corners and use the one that does not have the white
                side1 = self.cube.get_side(corner_pos.split("_")[0])
                side2 = self.cube.get_side(corner_pos.split("_")[1])
                correct_side = None

                if corner_info[1] in ["left", "right"]:
                    for row in side1:
                        if target_symbol in row:
                            correct_side = corner_pos.split("_")[1]
                            break

                    for row in side2:
                        if target_symbol in row:
                            correct_side = corner_pos.split("_")[0]
                            break
                elif corner_info[1] == "up":
                    up_dict = {
                        "top_left": "top",
                        "top_right": "right",
                        "bottom_right": "bottom",
                        "bottom_left": "left"
                    }
                    correct_side = up_dict[corner_pos]

                # Change perspective
                persp_dict = {
                    "top": "down",
                    "bottom": "up",
                    "right": "left",
                    "left": "right"
                }
                self.cube.change_perspective(persp_dict[correct_side])

                # Now rotate the front depending on which side was brought to front
                rotate_dict = {
                    "bottom": 0,
                    "right": 1,
                    "top": 2,
                    "left": 3
                }

                for _ in range(rotate_dict[correct_side]):
                    self.cube.rotate_whole()

                # Based on white position on the corner do certain algorithm
                match corner_info[1]:
                    case "up":
                        for _ in range(3):
                            self.right_algorithm()
                    case "right":
                        self.right_algorithm()
                    case "left":
                        self.left_algorithm()

                # break out of the for loop because perspectives and cubes have rotated
                break

            # Move white side back to back
            self.move_to_front("Y5")
            self.cube.rotate_big("front")

    def find_edge(self):
        pairs = {
            "top": [(3, 4), (2, 4), (1, 4)],
            "left": [(4, 3), (4, 2), (4, 1)],
            "right": [(4, 5), (4, 6), (4, 7)],
            "bottom": [(5, 4), (6, 4), (7, 4)],
        }

        for edge, positions in pairs.items():
            edge_piece_1 = (self.cube.cube[positions[0][0]][positions[0][1]])
            edge_piece_2 = (self.cube.cube[positions[1][0]][positions[1][1]])
            center_piece = (self.cube.cube[positions[2][0]][positions[2][1]])

            # Skip yellow edge
            if edge_piece_1[0] == "Y" or edge_piece_2[0] == "Y":
                continue

            if edge_piece_2[0] == center_piece[0]:
                return edge, positions

    def is_second_done(self) -> str:
        # Check horizontal
        hor_sides = [self.cube.get_side("top"), self.cube.get_side("bottom")]
        ver_sides = [self.cube.get_side("left"), self.cube.get_side("right")]

        for i, side in enumerate(hor_sides):
            main_color = side[1][1][0]
            edge_side = "top" if i == 0 else "bottom"

            if side[1][0][0] != main_color or side[1][2][0] != main_color:
                return edge_side

        for i, side in enumerate(ver_sides):
            main_color = side[1][1][0]
            edge_side = "left" if i == 0 else "right"

            if side[0][1][0] != main_color or side[2][1][0] != main_color:
                return edge_side

        return ""

    def fix_second(self, fix_info):
        # print(fix_info)
        self.change_side_and_rotate(fix_info, self.rotation_dir[fix_info])

        # Check which side algorithm to perform
        front_side = self.cube.get_side("front")
        mid = front_side[1][1][0]

        if front_side[1][0][0] != mid:
            self.second_layer_algo("left")
        elif front_side[1][2][0] != mid:
            self.second_layer_algo("right")

    def second_layer_algo(self, side):
        if side == "left":
            self.cube.slide_long("right", 3)
            self.left_algorithm()
            self.cube.change_perspective("right")
            self.right_algorithm()
        elif side == "right":
            self.cube.slide_long("left", 3)
            self.right_algorithm()
            self.cube.change_perspective("left")
            self.left_algorithm()

    def second_layer(self):
        # Loop over the 4 pedals of Y and search edge that has both sides non yellow
        # After rotate front until the edge counter square matches with the center
        # print(new_edge, edge_positions)
        self.move_to_front("Y5")
        rotate_counter = 0

        while True:
            edge_info = self.find_edge()

            # Check if no edge info, then either rotate the front or break if nothing to be found anymore
            if edge_info is None:
                if rotate_counter > 4:
                    break

                self.move_to_front("Y5")
                self.cube.rotate_big("front")
                rotate_counter += 1
                continue

            rotate_counter = 0
            new_edge, edge_positions = edge_info[0], edge_info[1]

            self.change_side_and_rotate(new_edge, self.rotation_dir[new_edge])

            # Based on where the edge needs to be moved run certain algorithm
            if self.cube.cube[2][4][0] == self.cube.cube[4][1][0]:
                self.second_layer_algo("left")
            elif self.cube.cube[2][4][0] == self.cube.cube[4][7][0]:
                self.second_layer_algo("right")

            self.move_to_front("Y5")

        # If second layer is not done after easy moves, fix wrong edge and try again
        fix_info = self.is_second_done()
        if fix_info != "":
            # print("layer not done")
            self.fix_second(fix_info)
            self.second_layer()

    def yellow_cross(self):
        def find_hooks() -> bool:
            front_face = self.cube.get_side("front")
            flattened_face = []

            for row in front_face:
                for col in row:
                    flattened_face.append(col)

            # All possible hooks
            hook_coordinates = [(1, 3), (1, 5), (3, 7), (5, 7)]

            for i in range(len(flattened_face)):
                if flattened_face[i][0] != "Y":
                    continue

                # Check if possible hook
                for candidate in hook_coordinates:
                    if candidate[0] == i and flattened_face[candidate[1]][0] == "Y":
                        return True

            return False

        def is_hook_corner() -> bool:
            front_face = self.cube.get_side("front")

            if front_face[0][1][0] == "Y" and front_face[1][0][0] == "Y":
                return True

            return False

        self.move_to_front("Y5")

        # Check if yellow cross already exists
        # Symbols can be --> dot, hook, line, cross
        current_big_symbol = "dot"
        index_with_yellow = []
        front_side = self.cube.get_side("front")

        for row in range(len(front_side)):
            for col in range(len(front_side[0])):
                order_num = row * (len(front_side[0])) + (col + 1)

                if order_num % 2 == 1:
                    continue

                if front_side[row][col][0] == "Y":
                    index_with_yellow.append(order_num - 1)

        # Find symbol from worst to best
        if find_hooks():
            current_big_symbol = "hook"

        # Check for line
        vertical_line = False
        horizontal_line = False
        if 1 in index_with_yellow and 7 in index_with_yellow:
            current_big_symbol = "line"
            vertical_line = True
        if 3 in index_with_yellow and 5 in index_with_yellow:
            current_big_symbol = "line"
            horizontal_line = True

        if horizontal_line and vertical_line:
            current_big_symbol = "cross"

        match current_big_symbol:
            case "cross":
                return
            case "line":
                # First make line horizontal
                if vertical_line:
                    self.cube.rotate_big("front")

                self.cube.change_perspective("up")
                self.cube.rotate_big("front")
                self.right_algorithm()

                for _ in range(3):
                    self.cube.rotate_big("front")

                self.cube.change_perspective("down")

            case "hook":
                # Rotate the front until 3 of the 4 left top squares are yellow
                while not is_hook_corner():
                    self.cube.rotate_big("front")

                self.cube.change_perspective("up")
                self.cube.rotate_big("front")
                self.right_algorithm()
                self.right_algorithm()

                for _ in range(3):
                    self.cube.rotate_big("front")

                self.cube.change_perspective("down")

            case "dot":
                self.cube.change_perspective("up")
                self.cube.rotate_big("front")
                self.right_algorithm()

                for _ in range(3):
                    self.cube.rotate_big("front")

                self.cube.change_perspective("down")

                # Recursive call
                self.yellow_cross()

    def niklas(self):
        self.cube.slide_long("up", 5, 5)
        for _ in range(3):
            self.cube.rotate_big("front")

        self.cube.slide_long("up", 3, 3)
        self.cube.rotate_big("front")
        self.cube.slide_long("down", 5, 5)
        for _ in range(3):
            self.cube.rotate_big("front")

        self.cube.slide_long("down", 3, 3)

    def sune(self):
        self.cube.slide_long("up", 5, 5)
        self.cube.rotate_big("front")
        self.cube.slide_long("down", 5, 5)
        self.cube.rotate_big("front")
        self.cube.slide_long("up", 5, 5)

        for _ in range(2):
            self.cube.rotate_big("front")

        self.cube.slide_long("down", 5, 5)

    def top_layer_edges(self) -> List[str]:
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        side_dict = {
            0: "top",
            1: "bottom",
            2: "right",
            3: "left"
        }
        # for example top, left, right, bottom
        aligned_edges = []

        # Go from center to directions to get the info
        for direction_index in range(4):
            current_position = [4, 4]
            current_direction = directions[direction_index]

            # Get into right position of the edge
            for distance_index in range(2):
                current_position[0] += current_direction[0]
                current_position[1] += current_direction[1]

            corner_square = self.cube.cube[current_position[0]][current_position[1]]

            current_position[0] += current_direction[0]
            current_position[1] += current_direction[1]

            center_square = self.cube.cube[current_position[0]][current_position[1]]

            # Make certain edge color and face center match
            if corner_square[0] != center_square[0]:
                continue

            aligned_edges.append(side_dict[direction_index])

        return aligned_edges

    def align_third_layer_edges(self):
        # Rotate the front until at least two top layer edges match
        while True:
            matching_top_edges = self.top_layer_edges()

            if len(matching_top_edges) >= 2:
                break

            self.cube.rotate_big("front")

        if len(matching_top_edges) == 4:
            return

        # Do sune algo to get two adjacent matching edges
        if "top" in matching_top_edges and "bottom" in matching_top_edges:
            self.sune()
        elif "left" in matching_top_edges and "right" in matching_top_edges:
            self.cube.rotate_whole()
            self.sune()

        # Rotate the cube until matching edges are on top and right
        while "top" not in matching_top_edges or "right" not in matching_top_edges:
            self.cube.rotate_whole()
            matching_top_edges = self.top_layer_edges()

        self.sune()

        while len(matching_top_edges) < 4 and len(matching_top_edges) != 0:
            self.cube.rotate_big("front")
            matching_top_edges = self.top_layer_edges()

    def get_correct_yellow_corners(self) -> List[str]:
        # Get all the corners that are in right spot
        correct_corners = []
        dir_dict = {
            0: "top-left",
            1: "bottom-left",

            2: "bottom-right",
            3: "top-right"
        }

        for i in range(4):
            left_center = self.cube.cube[4][1][0]
            top_center = self.cube.cube[1][4][0]
            current_pos = [3, 2]
            left_corner = self.cube.cube[current_pos[0]][current_pos[1]][0]
            current_pos[1] += 1
            middle_corner = self.cube.cube[current_pos[0]][current_pos[1]][0]
            current_pos[0] -= 1
            top_corner = self.cube.cube[current_pos[0]][current_pos[1]][0]
            temp_array = [left_corner, middle_corner, top_corner]

            # Check if the corner is in right spot
            if left_center not in temp_array or top_center not in temp_array:
                self.cube.rotate_whole()
                continue

            correct_corners.append(dir_dict[i])
            self.cube.rotate_whole()

        return correct_corners

    def is_done(self) -> bool:
        # Loop over all the faces and check that all the squares match the center
        for face in self.cube.sides_dict.keys():
            if face == "back2":
                continue

            side = self.cube.get_side(face)
            center_color = side[1][1][0]

            for row in side:
                for cell in row:
                    if cell[0] != center_color:
                        return False

        return True

    def is_bottom_right_solved(self) -> bool:
        # Look at the front face bottom right corner to see if it is solved
        front_bottom_middle = self.cube.cube[5][4][0]
        bottom_top_middle = self.cube.cube[6][4][0]
        right_bottom_middle = self.cube.cube[5][7][0]

        # check top
        if self.cube.cube[5][5][0] != front_bottom_middle:
            return False

        # check right
        if self.cube.cube[5][6][0] != right_bottom_middle:
            return False

        # check bottom
        if self.cube.cube[6][5][0] != bottom_top_middle:
            return False

        return True

    def solve_bottom_right_corners(self):
        # Put unsolved corner to bottom face right side and do right algo until corner solved
        # First change perspective right

        while True:
            corners_solved = 0
            # Keep sliding until bottom right corner not solved
            # If rotates 4 times means all corners are solved
            while self.is_bottom_right_solved():
                if corners_solved == 4:
                    return

                self.cube.slide_long("left", 5, 5)
                corners_solved += 1

            while not self.is_bottom_right_solved():
                self.right_algorithm()

    def third_layer(self):
        if self.is_done():
            return

        # Align the edges
        self.align_third_layer_edges()
        yellow_corners = self.get_correct_yellow_corners()

        if self.is_done():
            return

        # If none of the corners are right
        if len(yellow_corners) == 0:
            self.niklas()
            self.align_third_layer_edges()
            yellow_corners = self.get_correct_yellow_corners()

        # If less than 4 corners are correct
        if len(yellow_corners) < 4:
            while yellow_corners[0] != "bottom-left":
                self.cube.rotate_whole()
                yellow_corners = self.get_correct_yellow_corners()

            while len(self.get_correct_yellow_corners()) < 4:
                self.niklas()
                self.align_third_layer_edges()

        if self.is_done():
            return

        # Change perspective for corners and solve them
        self.move_to_front("W5")
        self.cube.change_perspective("up")
        self.solve_bottom_right_corners()

        # Slide the layer to right place
        while not self.is_done():
            self.cube.slide_long("right", 5, 5)

    def finalize(self):
        # To original orientation
        self.move_to_front("W5")

        while self.cube.cube[1][4][0] != "O":
            self.cube.rotate_whole()

    def solve(self):
        # First make daisy
        self.daisy()

        # White cross
        self.white_cross()

        # White corners
        self.white_corners()

        # Second layer
        self.second_layer()

        # Yellow cross
        self.yellow_cross()

        # Third layer
        self.third_layer()

        # Fix orientation
        self.finalize()
