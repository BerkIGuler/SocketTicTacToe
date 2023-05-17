import logging
import random

from config import admin_config
import socket
import consts

from logger import get_module_logger
from parsers import HTTPParser
from utils import TicTacToeHTTPCommand

import threading


class GameAdmin:
    current_players = []

    def __init__(self, tcp_config, logger):
        self.logger = logger
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((tcp_config.ip, tcp_config.port))
        self.client_sockets = []
        self.client_addrs = []
        self.current_turn = random.choice(["X", "O"])
        self.ttt = TicTacToe()

    def start_server(self):
        self.socket.listen()
        self.logger.info("Waiting for players to connect...")

        while True:
            client_socket, client_addr = self.socket.accept()
            self.logger.info(f"New connection from {client_addr}")

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_addr))
            client_thread.start()

    def handle_client(self, client_socket, client_addr):
        assigned = False

        try:
            if len(self.client_sockets) > 1:
                self.logger.error("No room for a new player!")

            else:
                # check join request first
                command = self._receive_command(client_socket)
                msg = HTTPParser(command).get_json_content()
                assert msg["type"] == "join", "must receive join request first"
                p_name = msg["player_name"]

                # add the new client to current lists
                self.client_sockets.append(client_socket)
                self.client_addrs.append(client_addr)

                while True:
                    if len(self.client_sockets) == 2 \
                            and client_socket in self.client_sockets \
                            and not assigned:
                        assigned = True
                        self._notify_client(client_socket, p_name)

                    if assigned:
                        self._start_the_game(
                            client_socket,
                            client_addr,
                            p_name)

        except Exception as e:
            self.logger.error(f"Error while handling client: {e}")
        finally:
            client_socket.close()

    def _start_the_game(self, client_socket, client_addr, name):
        self._send_turn(client_socket, client_addr, name)
        msg = self._receive_command(client_socket)
        msg = HTTPParser(msg).get_json_content()
        if self._valid_move(client_socket, msg):
            self._update_board(msg, client_socket)
        else:
            # self._send_invalid_move_msg()
            pass

    def _notify_client(self, client_socket, p_name):
        p_id, symbol = self._get_ip_and_sym(client_socket)
        http_resp = TicTacToeHTTPCommand().symbol_and_id(symbol, p_id)
        self.logger.info(f"Assigned ID {p_id} and symbol {symbol} to "
                         f"{p_name}")
        client_socket.sendall(http_resp)

    def _send_turn(self, client_socket, client_addr, name):
        client_ip = client_addr[0]
        p_id, symbol = self._get_ip_and_sym(client_socket)

        if symbol == self.current_turn:
            msg = TicTacToeHTTPCommand().turn(
                client_ip, p_id, symbol,
                board_state=TicTacToe.encode(self.ttt.board),
                your_turn=True
            )
            client_socket.sendall(msg)
        else:
            msg = TicTacToeHTTPCommand().turn(
                client_ip, p_id, symbol,
                board_state=TicTacToe.encode(self.ttt.board),
                your_turn=False
            )
            client_socket.sendall(msg)

        # self.current_turn = "X" if self.current_turn == "O" else "O"
        self.logger.info(f"Sent board info to {name}")

    def _valid_move(self, client_socket, msg):
        valid = False
        p_id, symbol = self._get_ip_and_sym(client_socket)
        if msg["type"] == "move" and int(msg["id"]) == p_id:
            row, col = int(msg["row"]), int(msg["col"])
            if self.ttt.validate_move((row, col)):
                valid = True
        return valid

    def _get_ip_and_sym(self, client_socket):
        p_id = self.client_sockets.index(client_socket)
        symbol = ["X", "O"][p_id]
        return p_id, symbol

    def _update_board(self, msg, client_socket):
        _, sym = self._get_ip_and_sym(client_socket)
        row, col = int(msg["row"]), int(msg["col"])
        self.ttt.update_board(sym, (row, col))
        print(self.ttt)

    @staticmethod
    def _receive_command(client_socket):
        msg = b""
        while True:
            chunk = client_socket.recv(consts.RECV_BYTE_SIZE)
            msg += chunk
            if HTTPParser(chunk).check_content_len():
                break

        return msg


class TicTacToe:
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
        if board:
            self.board = board
        else:
            self.board = [["-", "-", "-"],
                          ["-", "-", "-"],
                          ["-", "-", "-"]]

    @classmethod
    def encode(cls, board):
        flattened = sum(board, [])
        encoded_board = ".".join(flattened)
        return encoded_board

    @classmethod
    def decode(cls, board):
        chars = board.split(".")
        decoded_board = [chars[0:3], chars[3:6], chars[6:]]
        return cls(decoded_board)

    def update_board(self, sym, pos):
        if self.validate_move(pos) and sym.upper() in ["X", "O"]:
            row, col = pos
            self.board[row][col] = sym.upper()
            status = consts.VALID_MOVE
        else:
            status = consts.INVALID_MOVE

        if self._get_winner():
            winner = self._get_winner()
            if winner == "X":
                status = consts.WINNER_X
            elif winner == "O":
                status = consts.WINNER_O

        return status

    def _get_winner(self):
        winner = None
        winner_count = 0
        for cond in self.win_conds:
            values = []
            for pos in cond:
                i, j = pos
                values.append(self.board[i][j])

            if values == self.Xs:
                winner = "X"
                winner_count += 1
            elif values == self.Os:
                winner = "O"
                winner_count += 1

        if winner_count > 1:
            raise ValueError("Conflict in X and O positions")

        return winner

    def validate_move(self, move):
        valid = True
        row, col = move
        if move not in self.valid_moves or self.board[row][col] != "-":
            valid = False

        return valid

    def __repr__(self):
        ser = sum(self.board, [])
        formatted = """
        _____________
        | {0} | {1} | {2} | 
        | {3} | {4} | {5} |
        | {6} | {7} | {8} |
        """.format(*ser)
        return formatted


if __name__ == "__main__":
    logger = get_module_logger(
        logger_name=__name__,
        log_level=logging.INFO,
        file_path="logs/server.log"
    )

    # port = parse_port()
    # update_args(admin_config, **{"port": port})

    admin = GameAdmin(tcp_config=admin_config, logger=logger)
    admin.start_server()
