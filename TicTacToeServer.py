import logging
import random
import socket
import threading
import time

import consts
from config import admin_config, update_args
from logger import get_module_logger
from parsers import HTTPParser, parse_port
from utils import TicTacToeHTTPCommand, ConsoleOutput
from game_logic import TicTacToe


class TTTServer:
    std_out = ConsoleOutput()

    def __init__(self, tcp_config, logger_):
        """A server class to handle 2 TTTClient via threads"""
        self.logger = logger_
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((tcp_config.ip, tcp_config.port))

        self.client_sockets = []
        self.current_turn = random.choice(["X", "O"])
        self.ttt = TicTacToe()

    def start_server(self):
        """starts server IP and PORT in main thread"""
        self.socket.listen()
        self.logger.info("Waiting for two players to start the game...")
        while True:
            client_socket, client_addr = self.socket.accept()

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, ))
            client_thread.start()

    def handle_client(self, client_socket):
        """main driver for each client"""
        pid = None

        try:
            if len(self.client_sockets) > 1:
                self.logger.error("No room for a new player!")

            else:
                # check join request first
                command = self._receive_command(client_socket)
                msg = HTTPParser(command).get_json_content()
                assert msg["type"] == "post_join", "must receive join request first"

                self.client_sockets.append(client_socket)

                while True:
                    if len(self.client_sockets) == 2 and pid is None:
                        self._notify_client(client_socket)
                        self.std_out.print("The game is started")
                        pid, _ = self._get_pid_and_sym(client_socket)
                        next_player_id = ["X", "O"].index(self.current_turn)
                        self.std_out.print(f"Waiting for player {next_player_id}'s move")

                    if pid is not None:
                        game_done = self._next_round(pid, client_socket)
                        if game_done:
                            break

        except Exception as e:
            self.logger.error(f"Error while handling client: {e}")
            raise e
        finally:
            client_socket.close()

    def _next_round(self, pid, client_socket):
        """a function to implement the logic of each round"""
        next_player_id = ["X", "O"].index(self.current_turn)
        request = HTTPParser(
            self._receive_command(self.client_sockets[pid])
        ).get_json_content()

        if request["type"] == "get_result":
            self._send_result(pid)

        elif request["type"] == "get_turn":
            self._send_turn(pid)

        elif request["type"] == "post_leave":
            self._send_leave_response(pid)
            time.sleep(1)
            # get ready for next turn
            self.client_sockets.remove(client_socket)
            self.ttt = TicTacToe()
            self.current_turn = random.choice(["X", "O"])
            return True

        elif request["type"] == "post_move":
            _, sym = self._get_pid_and_sym(self.client_sockets[pid])
            row, col = int(request["row"]), int(request["col"])
            if self._valid_move(pid, request):
                self.logger.info(f'Received {sym} on ({row}, {col}). It is a legal move.')
                self._update_board(request, pid)
                self._send_response_move(
                    pid, desc="Move is valid",
                    s_code=200)
                self.current_turn = "X" if self.current_turn == "O" else "O"
                next_player_id = ["X", "O"].index(self.current_turn)
            else:
                self.logger.info(f'Received {sym} on ({row}, {col}). It is an illegal move.')
                self._send_response_move(
                    pid, desc="Invalid move!",
                    s_code=400)
            self.logger.info(f"Waiting for player {next_player_id}'s move")

        elif request["type"] == "post_leave":
            self._send_leave_response(pid)

    def _send_leave_response(self, pid):
        client_socket = self.client_sockets[pid]
        client_socket.sendall(
            TicTacToeHTTPCommand().response_leave(
                pid=pid,
                status_code=200
            )
        )

    def _send_result(self, pid):
        """sends game result to via client socket"""
        client_socket = self.client_sockets[pid]
        result = self.ttt.get_winner()
        if result == consts.TIE:
            msg = TicTacToeHTTPCommand().response_result(
                win_info="tie", status_code=200
            )
        elif result == consts.WINNER_X:
            msg = TicTacToeHTTPCommand().response_result(
                win_info="X", status_code=200
            )
        elif result == consts.WINNER_O:
            msg = TicTacToeHTTPCommand().response_result(
                win_info="O", status_code=200
            )
        else:
            msg = TicTacToeHTTPCommand().response_result(
                win_info="None", status_code=200
            )
        client_socket.sendall(msg)

    def _send_turn(self, pid):
        """sends current turn's symbol via client socket"""
        client_socket = self.client_sockets[pid]
        client_socket.sendall(TicTacToeHTTPCommand().response_turn(
            turn_info=self.current_turn,
            pid=pid,
            board_state=TicTacToe.encode(self.ttt.board),
            status_code=200
        ))

    def _send_response_move(self, pid, desc, s_code=200):
        """sends the response of a move message"""
        client_socket = self.client_sockets[pid]
        client_socket.sendall(TicTacToeHTTPCommand().response_move(
            desc=desc,
            status_code=s_code
        ))

    def _notify_client(self, client_socket):
        """notifies each client of their IDs and symbol at the beginning"""
        p_id, symbol = self._get_pid_and_sym(client_socket)
        http_resp = TicTacToeHTTPCommand().response_join(
            symbol, p_id,
            status_code=200
        )
        self.logger.info(f"A client is connected, and is "
                         f"assigned with the symbol {symbol} and ID={p_id}")
        client_socket.sendall(http_resp)

    def _valid_move(self, pid, msg):
        """returns True if a move is valid, else False"""
        valid = False
        if int(msg["id"]) == pid:
            row, col = int(msg["row"]), int(msg["col"])
            if self.ttt.validate_move((row, col)):
                valid = True
        return valid

    def _get_pid_and_sym(self, client_socket):
        """return player id and symbol corresponding the given socket"""
        p_id = self.client_sockets.index(client_socket)
        symbol = ["X", "O"][p_id]
        return p_id, symbol

    def _update_board(self, msg, pid):
        """inserts given symbol to requested position"""
        _, sym = self._get_pid_and_sym(self.client_sockets[pid])
        row, col = int(msg["row"]), int(msg["col"])
        _ = self.ttt.update_board(sym, (row, col))

    @staticmethod
    def _receive_command(client_socket):
        """receives bytes over the client until content length is reached"""
        msg = b""
        while True:
            chunk = client_socket.recv(consts.RECV_BYTE_SIZE)
            msg += chunk
            if HTTPParser(chunk).check_content_len():
                break
        return msg


if __name__ == "__main__":
    logger = get_module_logger(
        logger_name=__name__,
        log_level=logging.INFO,
        file_path="logs/server.log"
    )

    port = parse_port()
    update_args(admin_config, **{"port": port})

    admin = TTTServer(tcp_config=admin_config, logger_=logger)
    admin.start_server()
