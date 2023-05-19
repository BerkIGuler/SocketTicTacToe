import consts


class TicTacToe:
    """a class to implement basic TTT game logic"""
    valid_moves = [(0, 0), (0, 1), (0, 2),
                   (1, 0), (1, 1), (1, 2),
                   (2, 0), (2, 1), (2, 2)]

    win_conds = [[(0, 0), (1, 0), (2, 0)],
                 [(0, 1), (1, 1), (2, 1)],
                 [(0, 2), (1, 2), (2, 2)],
                 [(0, 0), (0, 1), (0, 2)],
                 [(1, 0), (1, 1), (1, 2)],
                 [(2, 0), (2, 1), (2, 2)],
                 [(0, 0), (1, 1), (2, 2)],
                 [(2, 0), (1, 1), (0, 2)]]

    Xs = ["X", "X", "X"]
    Os = ["O", "O", "O"]

    def __init__(self, board=None):
        """constructs a TTT object"""
        if board:
            self.board = board
        else:
            self.board = [["-", "-", "-"],
                          ["-", "-", "-"],
                          ["-", "-", "-"]]

    @classmethod
    def encode(cls, board):
        """converts board to string format"""
        flattened = sum(board, [])
        encoded_board = ".".join(flattened)
        return encoded_board

    @classmethod
    def decode(cls, board):
        """recovers a TTT object from encoded board status"""
        chars = board.split(".")
        decoded_board = [chars[0:3], chars[3:6], chars[6:]]
        return cls(decoded_board)

    def update_board(self, sym, pos):
        """inserts a character if move is valid"""
        if self.validate_move(pos) and sym.upper() in ["X", "O"]:
            row, col = pos
            self.board[row][col] = sym.upper()
        else:
            raise RuntimeError("Unexpected board state!!")

    def get_winner(self):
        """returns win, tie, None messages based on who won"""
        winner = None
        winner_count = 0
        for cond in self.win_conds:
            values = []
            for pos in cond:
                i, j = pos
                values.append(self.board[i][j])

            if values == self.Xs:
                winner = consts.WINNER_X
                winner_count += 1
            elif values == self.Os:
                winner = consts.WINNER_O
                winner_count += 1

        if winner_count > 1:
            raise ValueError("Conflict in X and O positions")

        if self._is_full() and winner is None:
            return consts.TIE

        return winner

    def _is_full(self):
        """checks if all positions are filled"""
        flattened = sum(self.board, [])
        return not ("-" in flattened)

    def validate_move(self, move):
        """returns True for valid moves"""
        valid = True
        row, col = move
        if move not in self.valid_moves or self.board[row][col] != "-":
            valid = False

        return valid

    def __repr__(self):
        """determines the formatting during printing"""
        ser = sum(self.board, [])
        formatted = """
        _____________
        | {0} | {1} | {2} | 
        | {3} | {4} | {5} |
        | {6} | {7} | {8} |
        """.format(*ser)
        return formatted
