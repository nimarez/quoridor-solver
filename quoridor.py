import copy
# State model: 
# - player1 pawn position, player2 pawn position
# - A board graph, with positions (1, 1)[top left corner] through (9, 9)[bottom right corner]
#  as vertices, and edges between adjacent vertices. A "wall" is an object that cuts off two edges.

# Rules:
# - Player that gets their pawn to the other side the fastest wins
# - Players can place horizontal and vertical walls, NOT diagonal
# - Players cannot place walls on the outside border
# - Players cannot move through walls
# - Both pawns always have to have a path to the other side
# - Walls cannot intersect(how to check?):
#    - Walls cannot cut off an edge that already been cut
#    - Walls cannot dissect another wall
# - Adjacent pawns can jump over each other(a good move)


class Wall:
    def __init__(self, lower_corner, upper_corner, direc):
        assert direc == "h" or direc == "v"
        assert lower_corner[0] < upper_corner[0] and lower_corner[1] < upper_corner[1]
        self.lower_corner = lower_corner
        self.upper_corner = upper_corner
        self.direc = direc

    def __str__(self):
        s = ["lower corner: " + str(self.lower_corner) + ", ", "upper corner: " + str(self.upper_corner) + ", ",
             "direction: " + str(self.direc)]
        return "".join(s)

    @staticmethod
    def all_walls():
        walls = []
        for i in range(1, 9):
            for j in range(1, 9):
                for direc in ["h", "v"]:
                    wall = Wall((i, j), (i + 1, j + 1), direc)
                    walls.append(wall)
        return walls

    def edges_cut(self):
        """
        Gives the edges that this wall cuts
        """
        if self.direc == "h":
            edge1 = (self.lower_corner, (self.lower_corner[0], self.lower_corner[1] + 1))
            edge2 = (self.upper_corner, (self.upper_corner[0], self.upper_corner[1] - 1))
            return edge1, edge2
        if self.direc == "v":
            edge1 = (self.lower_corner, (self.lower_corner[0] + 1, self.lower_corner[1]))
            edge2 = (self.upper_corner, (self.upper_corner[0] - 1, self.upper_corner[1]))
            return edge1, edge2

    def crossing_walls(self):
        """
        Gives the walls that cannot coexist with this wall
        """
        walls = [Wall(self.lower_corner, self.upper_corner, "v" if self.direc == "h" else "h")]
        if self.direc == "h":
            new_lc = (self.lower_corner[0] + 1, self.lower_corner[1])
            new_up = (self.upper_corner[0] + 1, self.upper_corner[1])
            walls.append(Wall(new_lc, new_up, "h"))
            new_lc = (self.lower_corner[0] - 1, self.lower_corner[1])
            new_up = (self.upper_corner[0] - 1, self.upper_corner[1])
            walls.append(Wall(new_lc, new_up, "h"))
        if self.direc == "v":
            new_lc = (self.lower_corner[0], self.lower_corner[1] + 1)
            new_up = (self.upper_corner[0], self.upper_corner[1] + 1)
            walls.append(Wall(new_lc, new_up, "v"))
            new_lc = (self.lower_corner[0], self.lower_corner[1] - 1)
            new_up = (self.upper_corner[0], self.upper_corner[1] - 1)
            walls.append(Wall(new_lc, new_up, "v"))
        return walls

    def __eq__(self, other):
        if not other:
            return False
        return self.lower_corner == other.lower_corner and \
               self.upper_corner == other.upper_corner and \
               self.direc == other.direc


class Board:
    def __init__(self, p1=(5, 1), p2=(5, 9), graph=None, walls=None):
        self.p1 = p1
        self.p2 = p2
        if graph:
            self.graph = graph
        else:
            self.graph = {}
            for i in range(1, 9 + 1):
                for j in range(1, 9 + 1):
                    self.graph[(i, j)] = []
                    for inc in [-1, 1]:
                        if 1 <= i + inc <= 9:
                            self.graph[(i, j)].append((i + inc, j))
                        if 1 <= j + inc <= 9:
                            self.graph[(i, j)].append((i, j + inc))
        if walls:
            for wall in walls:
                edges_to_remove = wall.edges_cut()
                for edge in edges_to_remove:
                    v1, v2 = edge
                    if v2 in self.graph[v1]:
                        self.graph[v1].remove(v2)
                    if v1 in self.graph[v2]:
                        self.graph[v2].remove(v1)
            self.walls = walls
        else:
            self.walls = []

    def __deepcopy__(self, memo):
        copied_graph = copy.deepcopy(self.graph)
        copied_walls = copy.deepcopy(self.walls)
        return Board(self.p1, self.p2, copied_graph, copied_walls)

    def __str__(self):
        """
        Print the entire state. Currently prints an empty board. TODO: this is hard...
        """
        s = []
        offsets = []
        for i in range(1, 18):
            # Draw squares and parts of vertical walls if odd
            # Draw horizontal walls and parts of vertical walls if even
            if i % 2 == 1:
                y = i // 2 + 1
                run, idx = 0, 0
                for x in range(1, 9):
                    # boolean for vertical walls
                    put_already = False
                    # Put future marker for horizontal walls
                    if Wall((x, y), (x + 1, y + 1), "h") in self.walls:
                        offsets.append([run, "-----", 1, 5])

                    # we have to do this no matter what
                    if self.p1 == (x, y):
                        square_char = "1"
                    elif self.p2 == (x, y):
                        square_char = "2"
                    else:
                        square_char = "o"

                    s.append(square_char)
                    s.append(" ")
                    run += 2

                    # Put in obligatory vertical walls
                    if Wall((x, y), (x + 1, y + 1), "v") in self.walls:
                        if idx < len(offsets) and run == offsets[idx][0]:
                            offsets[idx][2] -= 1
                            if offsets[idx][2] == 0:
                                offsets.pop(idx)
                            else:
                                idx += 1
                        offsets.append([run, "|", 2, 1])
                        s.append("|")
                        run += 1
                        put_already = True

                    # Check for leftover vertical walls from before
                    if idx < len(offsets):
                        if run == offsets[idx][0] and not put_already:
                            s.append("|")
                            run += 1
                            offsets[idx][2] -= 1
                            if offsets[idx][2] == 0:
                                offsets.pop(idx)
                            else:
                                idx += 1
                            put_already = True

                    if put_already:
                        s.append(" ")
                        run += 1
                    else:
                        s.append("  ")
                        run += 2

                if self.p1 == (9, y):
                    square_char = "1"
                elif self.p2 == (9, y):
                    square_char = "2"
                else:
                    square_char = "o"
                s.append(square_char)
            else:
                run, idx = 0, 0
                # For lines in between
                tilt = 1
                while run < 40 and idx < len(offsets):
                    if offsets[idx][2] == 0:
                        idx += 1
                    elif run == offsets[idx][0] + tilt and offsets[idx][1] == "-----":
                        tilt += 1
                        s.append("----")
                        offsets[idx][2] -= 1
                        run += offsets[idx][3]
                        if offsets[idx][2] == 0:
                            offsets.pop(idx)
                        else:
                            idx += 1
                    elif run == offsets[idx][0]:
                        s.append(offsets[idx][1])
                        offsets[idx][2] -= 1
                        run += offsets[idx][3]
                        if offsets[idx][2] == 0:
                            offsets.pop(idx)
                        else:
                            idx += 1
                    else:
                        s.append(" ")
                        run += 1
            s.append("\n")
        return "".join(s)

    def move_pawn(self, player, destination):
        """
        Moves the pawn and creates a NEW board
        """
        copied_board = copy.deepcopy(self)
        if player == 1:
            copied_board.p1 = destination
        elif player == 2:
            copied_board.p2 = destination
        return copied_board

    def put_wall(self, wall):
        """
        Takes in a board, and a wall, and returns a NEW board with the wall
        placed on it.
        """
        assert isinstance(wall, Wall), "argument has to be a wall"
        copied_board = copy.deepcopy(self)
        copied_graph = copied_board.graph
        copied_walls = copied_board.walls
        copied_walls.append(wall)
        edges_to_remove = wall.edges_cut()
        for edge in edges_to_remove:
            v1, v2 = edge
            if v2 in copied_graph[v1]:
                copied_graph[v1].remove(v2)
            if v1 in copied_graph[v2]:
                copied_graph[v2].remove(v1)
        return copied_board

    @staticmethod
    def is_connected(graph, s, t):
        queue = [s]
        visited = set()
        while queue:
            v = queue.pop(0)
            if v == t:
                return True
            visited.add(v)
            for n in graph[v]:
                if n not in visited:
                    queue.append(n)
        return False

    def is_valid(self):
        """
        A board is invalid if any one of the players is blocked. Two sentinel vertices
        at the end of the board are used to test connectivity to at least one of the
        end squares.
        """
        # Add the two sentinel vertices, with DIRECTIONAL edges
        # (0, 0) is 1's sentinel, (10, 10) is 2's sentinel
        # in order for board to be valid, 1 has to be able to reach (10, 10)
        # and 2 has to be able to reach (0, 0)
        copied_graph = copy.deepcopy(self.graph)
        copied_graph[(0, 0)] = []
        for i in range(1, 10):
            copied_graph[(i, 1)].append((0, 0))

        copied_graph[(10, 10)] = []
        for i in range(1, 10):
            copied_graph[(i, 9)].append((10, 10))

        return Board.is_connected(copied_graph, self.p1, (10, 10)) and Board.is_connected(copied_graph, self.p2, (0, 0))


# ws = []
# for i in range(1, 9):
#     for j in range(1, 2):
#         if i % 2 == 0:
#             ws.append(Wall((i, j), (i + 1, j + 1), "h"))
# # ws.append(Wall((5, 2), (6, 3), "h"))
# b = Board(walls=ws)
# print(b.graph)
# print(b)
# print(b.is_valid())


class Move:
    def __init__(self, move_type, data):
        self.move_type = move_type
        self.data = data

    def __str__(self):
        s = []
        if self.move_type == "pawn":
            s.append("pawn to " + str(self.data))
        elif self.move_type == "wall":
            s.append("wall on " + str(self.data))
        return "".join(s)

    def __repr__(self):
        return self.__str__()


def memo(f):
    cache = {}

    def func(x):
        if x not in cache:
            cache[x] = f(x)
        return cache[x]
    return func


class State:
    def __init__(self, turn, p1_walls, p2_walls, board, avail_walls):
        # turn, either 1 or 2
        self.turn = turn
        # number of walls left for p1
        self.p1_walls = p1_walls
        # number of walls left for p2
        self.p2_walls = p2_walls
        # the board, represented as an adjacency list
        if not board:
            self.board = Board()
        else:
            self.board = board
        # available walls, used only for speeding up generate_moves
        if not avail_walls:
            self.avail_walls = Wall.all_walls()
        else:
            self.avail_walls = copy.deepcopy(avail_walls)
        self.walls = [wall for wall in Wall.all_walls() if wall not in self.avail_walls]

    def __str__(self):
        s = [self.board.__str__(), "\n", "It is player ", str(self.turn), "'s turn", "\n", "# of walls left for player 1: " + str(self.p1_walls) + "\n",
             "# of walls left for player 2: " + str(self.p2_walls) + "\n"]
        return "".join(s)

    @staticmethod
    def other_turn(turn):
        return 1 if turn == 2 else 2

    def primitive_value(self):
        """
        If the your pawn has reached the opposite side, you win.
        If your opponent's has, you lose
        """
        if self.board.p1[1] == 9:
            return "win" if self.turn == 1 else "lose"
        if self.board.p2[1] == 1:
            return "win" if self.turn == 2 else "lose"
        return "not_primitive"

    def generate_moves(self):
        """
        There are two types of moves: wall moves and pawn moves.
        What returned will be dictionary keyed by "wall" and "pawn",
        which will have the wall and pawn moves, respectively.
        """
        player = self.board.p1 if self.turn == 1 else self.board.p2
        moves = [Move("pawn", square) for square in self.board.graph[player]]
        for square in self.board.graph[player]:
            
        for wall in self.avail_walls:
            # peek the move and see if it blocks off any of the players
            new_board = self.board.put_wall(wall)
            if new_board.is_valid():
                moves.append(Move("wall", wall))
        print(moves)
        return moves

    def do_move(self, move):
        print(move)
        assert isinstance(move, Move), "move has to belong to the Move class"
        if move.move_type == "pawn":
            next_board = self.board.move_pawn(self.turn, move.data)
            return State(State.other_turn(self.turn), self.p1_walls, self.p2_walls, next_board, self.avail_walls)

        elif move.move_type == "wall":
            wall = move.data
            next_board = self.board.put_wall(wall)
            new_avail_walls = self.avail_walls.remove(wall)
            if self.turn == 1:
                new_p1_walls = self.p1_walls - 1
            elif self.turn == 2:
                new_p2_walls = self.p2_walls - 1

            return State(State.other_turn(self.turn), new_p1_walls, new_p2_walls, next_board, new_avail_walls)

    @memo
    def solve(self):
        print(self)
        value = self.primitive_value()
        if value != "not_primitive":
            return value, 0
        children = []
        for move in self.generate_moves():
            next_state = self.do_move(move)
            children.append(next_state.solve())

        win_list = [child for child in children if child[0] == "lose"]
        if win_list:
            best_win = min(win_list, key=lambda x: x[1])
            return "win", best_win[1] + 1
        tie_list = [child for child in children if child[0] == "tie"]

        if tie_list:
            best_tie = min(tie_list, key=lambda x: x[1])
            return "tie", best_tie[1] + 1
        else:
            best_lose = max(children, key=lambda x: x[1])
            return "lose", best_lose[1] + 1


start_state = State(1, 10, 10, Board(), None)
start_state.solve()






# def DoMove(state, move):
#     pass
#
#
# def GenerateMoves(state):
#     pass
#
#
# def PrimitiveValue(state):
#     pass


# # Testing
# solve = MakeSolver(DoMove, GenerateMoves, PrimitiveValue)
# print(solve(start_pos))
