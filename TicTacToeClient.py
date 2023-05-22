import logging
import socket
import time

import consts
from parsers import HTTPParser, parse_port
from config import player_config, sample_name, update_args
from utils import TicTacToeHTTPCommand, ConsoleOutput
from logger import get_module_logger
from TicTacToeServer import TicTacToe


class TTTClient:
    def __init__(self, name, logger, tcp_cfg):
        """A client class to playe TTT on TTTServer"""
        self.p_id = None
        self.p_sym = None
        self.logger = logger
        self.name = name
        self.tcp_cfg = tcp_cfg
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board = None

    def join(self):
        """Sends join request and waits for symbol and id assignment"""
        try:
            self.socket.connect((self.tcp_cfg.ip, self.tcp_cfg.port))
            self.logger.info(f"{self.name} sent a joining request")
            message = TicTacToeHTTPCommand().post_join(
                pname=self.name, ip=self.tcp_cfg.ip
            )
            self.socket.sendall(message)
        except Exception as e:
            self.logger.error(f"Could not connect to the server, {e}")
        self._assign_id_and_sym()

    def _assign_id_and_sym(self):
        """assigns id and sym to client"""
        response = self._receive_resp()
        content = HTTPParser(response).get_json_content()
        if content["type"] == "response_join":
            self.p_id = content["id"]
            self.p_sym = content["sym"]
        self.logger.info(f"{self.name} joined the game with id {self.p_id} and symbol {self.p_sym}")
        self.logger.info(f"Game starts...")

    def play(self):
        """main loop implementing client-side game logic"""
        other_id = "1" if str(self.p_id) == "0" else "0"
        std_out = ConsoleOutput()
        while True:
            time.sleep(0.25)  # sleep for some time to prevent overload
            result = self._get_winner()
            if result != "None":
                if result in ["X", "O"]:
                    print(f"{result} won!!")
                elif result == "tie":
                    print(f"It's a tie!!")
                self._send_leave()
                break

            turn = self._get_turn()

            if turn == self.p_sym:
                print(self.board)
                print("Your turn")
                row, col = self._get_user_input()
                if col is not None:
                    self._send_move(row, col)
                std_out.flush()
            else:
                std_out.print(self.board, f"Player {other_id}'s turn!!")

    def _get_turn(self):
        """requests turn info from server"""
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
            self.board = TicTacToe().decode(resp["board_state"])
        else:
            self.logger.error("Invalid turn info")
            status = None

        return status

    def _get_winner(self):
        """requests winner info from server"""
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

    def _get_user_input(self):
        """reads user input from stdin until success"""
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

    def _send_move(self, row, col):
        """sends a TTT move to the server and reports status if necessary"""
        message = TicTacToeHTTPCommand().post_move(
            row=row, col=col, pid=self.p_id, server_ip=self.tcp_cfg.ip
        )
        self.socket.sendall(message)
        status_code = HTTPParser(self._receive_resp()).get_status()
        if status_code == "400":
            print("Fill an unoccupied entry within board")
        elif status_code != "200":
            self.logger.error('Unexpected behavior....')

    def _send_leave(self):
        """sends a TTT leave request to the server"""
        message = TicTacToeHTTPCommand().post_leave(
            pid=self.p_id, server_ip=self.tcp_cfg.ip
        )
        self.socket.sendall(message)
        status_code = HTTPParser(self._receive_resp()).get_status()
        if status_code == "200":
            print("Left the game...")
        else:
            self.logger.error('Could not leave successfully...')


    def _receive_resp(self):
        """receives responses from server"""
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

    port = parse_port()
    update_args(player_config, **{"port": port})

    player_1 = TTTClient(name=sample_name(), logger=logger, tcp_cfg=player_config)
    player_1.join()
    player_1.play()
