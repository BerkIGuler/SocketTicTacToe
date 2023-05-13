import logging
import socket
import consts

from parsers import parse_port, HTTPParser
from config import player_config, update_args
from utils import TicTacToeHTTPCommand
from logger import get_module_logger


class Player:
    def __init__(self, name, logger, tcp_cfg):
        """connect to the ttt server"""
        self.logger = logger
        self.name = name
        self.tcp_cfg = tcp_cfg
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def join(self):
        try:
            self.socket.connect((self.tcp_cfg.ip, self.tcp_cfg.port))
            self.logger.info(f"Player sent join request!!")
            message = TicTacToeHTTPCommand().join_request(
                p_name=self.name, ip=self.tcp_cfg.ip
            )
            self.socket.sendall(message)
        except Exception as e:
            self.logger.error(f"Could not connect to the server, {e}")
        response = self._receive_symbol()
        content = HTTPParser(response).get_content()
        print(type(content))
        print(content)

    def _receive_symbol(self):
        response = b""
        while True:
            chunk = self.socket.recv(consts.RECV_BYTE_SIZE)
            if len(chunk) == 0:
                break
            response += chunk
        return response


if __name__ == "__main__":
    logger = get_module_logger(
        __name__,
        log_level=logging.INFO,
        file_path="./logs/client.log"
    )
    # port = parse_port()
    # update_args(player_config, **{"port": port})

    player_1 = Player(name="Berkay", logger=logger, tcp_cfg=player_config)
    player_1.join()



