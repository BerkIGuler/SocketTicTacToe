import socket
import consts

from parsers import parse_port
from config import player_config, update_args
from utils import HTTPParser


class Player:
    def __init__(self, name, logger):
        """connect to the ttt server"""
        self.logger = logger
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.info(f"Player {name} online")

    def join(self, tcp_cfg):
        try:
            self.socket.connect((tcp_cfg.ip, tcp_cfg.port))
            self.logger.info(f"Player sent join request!!")
            message = TicTacToeHTTPCommand().join_request(
                p_name=self.name, ip=tcp_config.ip
            )
            self.socket.sendall(message)
        except Exception as e:
            self.logger.error(f"Could not connect to the server, {e}")
        response = self._receive_symbol()
        content = HTTPParser(response).get_content()
        print(type(content))

    def _receive_symbol(self):
        response = b""
        while True:
            chunk = self.socket.recv(consts.RECV_BYTE_SIZE)
            if len(chunk) == 0:
                break
            response += chunk
        return response


class TicTacToeHTTPCommand():
    join_request_body = {
        "type": "",
        "player_name": "",
    }

    base_http_post = "POST / HTTP/1.1\r\n" \
                     + "Host: {ip}\r\n"\
                     + "Content-Type: application/json\r\n"\
                     + "Content-Length: {con_len}\r\n\r\n"

    base_http_get = "GET / HTTP/1.1\r\n" \
                    + "Host: {ip}\r\n" \
                    + "Accept: application/json\r\n\r\n"

    def __init__(self):
        self.type = type

    def join_request(self, p_name, ip):
        body = self.join_request_body.copy()
        body["player_name"] = p_name
        body["type"] = "join"
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(**{"ip": ip, "con_len": body_len})
        http_request = headers + body

        return http_request


if __name__ == "__main__":
    pass
    # port = parse_port()
    # update_args(tcp_config, **{"port": port})
    # print(tcp_config)

    # base_http_post = "POST / HTTP/1.1\r\n" \
    #                  + "Host: {ip}\r\n"\
    #                  + "Content-Type: application/json"\
    #                  + "Content-Length: 80"
    # print(base_http_post.format(**{"ip": 122}))

    # http_command = TicTacToeHTTPCommand(type="test")
    # http_command.create_join_request("ronaldo", "1.2.3.4")



