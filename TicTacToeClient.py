import logging
import socket
import consts

from parsers import parse_port, HTTPParser
from config import player_config, update_args, sample_name
from utils import TicTacToeHTTPCommand
from logger import get_module_logger
from TicTacToeServer import TicTacToe


class Player:
    def __init__(self, name, logger, tcp_cfg):
        """connect to the ttt server"""
        self.p_id = None
        self.p_sym = None
        self.logger = logger
        self.name = name
        self.tcp_cfg = tcp_cfg
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def join(self):
        try:
            self.socket.connect((self.tcp_cfg.ip, self.tcp_cfg.port))
            self.logger.info(f"{self.name} sent a joining request")
            message = TicTacToeHTTPCommand().join_request(
                p_name=self.name, ip=self.tcp_cfg.ip
            )
            self.socket.sendall(message)
        except Exception as e:
            self.logger.error(f"Could not connect to the server, {e}")
        self._assign_id_and_sym()

    def _assign_id_and_sym(self):
        response = self._receive_symbol()
        content = HTTPParser(response).get_json_content()
        if content["type"] == "join":
            self.p_id = content["player_id"]
            self.p_sym = content["player_sym"]
        self.logger.info(f"{self.name} joined the game with id {self.p_id} and symbol {self.p_sym}")
        self.logger.info(f"Waiting for the game to start...")

    def play(self):
        while True:
            response = self._receive_symbol()
            content = HTTPParser(response).get_json_content()
            if content["type"] == "your_turn":
                self._validate_turn(content)
                board_state = content["board_state"]
                board = TicTacToe.decode(board_state)
                print(board)
                row, col = self._get_user_input()
                self._send_move(row, col)

            elif content["type"] == "wait_turn":
                board_state = content["board_state"]
                board = TicTacToe.decode(board_state)
                print(board)
                print("Wait for your turn...")

    @staticmethod
    def _get_user_input():
        user_input = input("Enter your move in x,y format:")
        try:
            row, col = map(int, user_input.split(","))
        except Exception as e:
            raise e
        return row, col

    def _validate_turn(self, msg):
        assert msg["sym"] == self.p_sym
        assert int(msg["id"]) == self.p_id

    def _send_move(self, row, col):
        message = TicTacToeHTTPCommand().move(
            row=row, col=col, p_id=self.p_id, ip=self.tcp_cfg.ip
        )
        self.socket.sendall(message)

    def _receive_symbol(self):
        resp = b""
        while True:
            chunk = self.socket.recv(consts.RECV_BYTE_SIZE)
            resp += chunk
            if HTTPParser(chunk).check_content_len():
                break
        return resp


if __name__ == "__main__":
    logger = get_module_logger(
        __name__,
        log_level=logging.INFO,
        file_path="./logs/client.log"
    )

    # port = parse_port()
    # update_args(player_config, **{"port": port})

    player_1 = Player(name=sample_name(), logger=logger, tcp_cfg=player_config)
    player_1.join()
    player_1.play()