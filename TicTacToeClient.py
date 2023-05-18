import logging
import socket

from parsers import HTTPParser
from config import player_config, sample_name
from utils import TicTacToeHTTPCommand
from logger import get_module_logger
from TicTacToeServer import TicTacToe
import consts


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
        self.logger.info(f"Game starts...")

    def play(self):
        other_id = "1" if self.p_id == "0" else "0"
        while True:
            response = self._receive_symbol()
            http_parser = HTTPParser(response)
            content = http_parser.get_json_content()
            if content["type"] == "your_turn":
                self._validate_turn(content)
                print("Turn information: Your Turn!")
                print("State of the board")

                board_state = content["board_state"]
                board = TicTacToe.decode(board_state)
                print(board)

                row, col = self._get_user_input()
                if col is not None:
                    self._send_move(row, col)
                else:
                    assert row == consts.STATUS
                    self._request_status()

            elif content["type"] == "wait_turn":
                self._validate_turn(content)
                print(f"Turn information: Player {other_id}'s turn!"
                      + f" (Wait for player {other_id}'s move)")
                print("State of the board")

                board_state = content["board_state"]
                board = TicTacToe.decode(board_state)
                print(board)

            elif content["type"] == "move_status":
                status_code = http_parser.get_status()
                desc = content["desc"]
                if status_code == "400":
                    print(desc)
                    row, col = self._get_user_input()
                    if col is not None:
                        self._send_move(row, col)
                    else:
                        assert row == consts.STATUS
                        self._request_status()

    def _request_status(self):
        msg = TicTacToeHTTPCommand().status_request(self.tcp_cfg.ip)
        self.socket.sendall(msg)

    def _get_user_input(self):
        success = False
        vals = None
        while not success:
            success = True
            user_input = input("Enter your move in x,y format or type status to request game info:")
            try:
                row, col = map(int, user_input.split(","))
                vals = row, col
            except Exception as e:
                if user_input.strip() == "status":
                    vals = consts.STATUS, None
                else:
                    print("Invalid move")
                    self.logger.error(e)
                    success = False
        return vals

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
