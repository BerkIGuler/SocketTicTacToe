from config import admin_config
import socket
import consts


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

    def _receive_command(self):
        if self.client_socket:
            cmd = b""
            while True:
                chunk = self.client_socket.recv(consts.RECV_BYTE_SIZE)
                if len(chunk) == 0:
                    break
                cmd += chunk
            return cmd.decode("utf-8").strip()
        else:
            raise ConnectionRefusedError("Client socket not created yet...")
        

