import logging

from config import admin_config, update_args
import socket
import consts

from logger import get_module_logger
from parsers import parse_port, HTTPParser


class GameAdmin:
    def __init__(self, tcp_config, logger):
        self.logger = logger
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((tcp_config.ip, tcp_config.port))
        self.client_socket, self.client_addr = None, None

    def start_server(self):
        self.socket.listen()
        self.logger.info("Waiting for players to connect")
        self.client_socket, self.client_addr = self.socket.accept()
        self.logger.info(f"New connection from {self.client_addr}")

    def new_game(self):
        self.logger.info("Starting a new game...")
        command = self._receive_command()
        cmd_type = HTTPParser(command).get_json_content()["type"]
        if cmd_type == "join":


    def respond_symbol_and_id(self):

    def _receive_command(self):
        if self.client_socket:
            chunk = self.client_socket.recv(consts.RECV_BYTE_SIZE)
            msg = chunk
            while not HTTPParser(chunk).check_content_len():
                chunk = self.client_socket.recv(consts.RECV_BYTE_SIZE)
                msg += chunk
        else:
            raise ConnectionRefusedError("Client socket not created yet...")

        return msg


class TicTacToe:
    valid_moves = [(0,0), (0,1), (0,2),
                   (1,0), (1,1), (1,2),
                   (2,0), (2,1), (2,2)]
    def __int__(self):
        self.board = [["-", "-", "-"],
                      ["-", "-", "-"],
                      ["-", "-", "-"]]

    def update_board(self, sym, pos):
        validity = consts.VALID_MOVE
        if self._validate_move(pos):
            row, col = pos
            self.board[row][col] = sym
        else:
            validity = consts.INVALID_MOVE
        return validity

    def _validate_move(self, move):
        valid = True
        row, col = move
        if move not in self.valid_moves:
            valid = False

        if self.board[row][col] != "-":
            valid = False

        return valid


class Player:
    def __init__(self, id, name, symbol):
        self.id = id
        self.name = name
        self.symbol = symbol


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
