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
        self.board = None

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
            result = self._get_winner()
            if result in ["X", "O", "tie"]:
                print(f"Game ended with result {result}")
                break

            turn = self._get_turn()
            if turn:
                print(self.board)

            if turn == self.p_sym:
                print("Your turn")
                row, col = self._get_user_input()
                if col:
                    self._send_move(row, col)
                elif row == consts.STATUS:
                    turn = self._get_turn()
                    print(self.board)
            else:
                print(f"Player {other_id}'s turn!!")

    def _get_turn(self):
        msg = TicTacToeHTTPCommand().get_turn(
            server_ip=self.tcp_cfg.ip, pid=self.p_id
        )
        self.socket.sendall(msg)
        resp = HTTPParser(
            self._receive_resp()
        ).get_json_content()
        assert resp["type"] == "response_turn"
        if resp["turn"] in ["O", "X"]:
            status = resp["turn"]
            self.board = TicTacToe().decode(resp["board_status"])
        else:
            self.logger.error("Invalid turn info")
            status = None

        return status



    def _get_winner(self):
        msg = TicTacToeHTTPCommand().get_result(
            server_ip=self.tcp_cfg.ip, pid=self.p_id
        )

        self.socket.sendall(msg)
        resp = HTTPParser(
            self._receive_resp()
        ).get_json_content()
        assert resp["type"] == "response_result"
        if resp["win_info"] in ["X", "O", "tie", "None"]:
            status = resp["win_info"]
        else:
            self.logger.error("Invalid win_info")
            status = None

        return status

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

    def _receive_resp(self):
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
