import logging

from config import admin_config, update_args
import socket
import consts

from logger import get_module_logger
from parsers import parse_port, HTTPParser
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

    def start_server(self):
        self.socket.listen()
        self.logger.info("Waiting for players to connect...")

        while True:
            client_socket, client_addr = self.socket.accept()
            self.logger.info(f"New connection from {client_addr}")
            self.client_sockets.append(client_socket)
            self.client_addrs.append(client_addr)

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_addr))
            client_thread.start()

    def handle_client(self, client_socket, client_addr):
        try:
            while True:
                command = self._receive_command(client_socket)
                msg = HTTPParser(command).get_json_content()

                if msg["type"] == "join":
                    if len(self.current_players) > 1:
                        self.logger.error("No room for a new player!")
                        self.client_sockets.remove(client_socket)
                        self.client_addrs.remove(client_addr)
                        break
                    else:
                        player_name = msg["player_name"]
                        self.current_players.append(player_name)
                        self.respond_symbol_and_id(client_socket)

                    if len(self.current_players) == 2:
                        self._start_the_game(client_socket)

        except Exception as e:
            self.logger.error(f"Error while handling client: {e}")
        finally:
            client_socket.close()

    def respond_symbol_and_id(self, client_socket):
        new_p_id = len(self.current_players) - 1
        symbol = ["X", "O"][new_p_id]
        http_resp = TicTacToeHTTPCommand().symbol_and_id(symbol, new_p_id)
        self.logger.info(f"Assigned ID {new_p_id} and symbol {symbol} to "
                         f"{self.current_players[new_p_id]}")
        client_socket.sendall(http_resp)

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

    def __init__(self):
        self.board = [["-", "-", "-"],
                      ["-", "-", "-"],
                      ["-", "-", "-"]]

    def update_board(self, sym, pos):
        if self._validate_move(pos) and sym.upper() in ["X", "O"]:
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

    def _validate_move(self, move):
        valid = True
        row, col = move
        if move not in self.valid_moves:
            valid = False

        if self.board[row][col] != "-":
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
    admin.new_game()
