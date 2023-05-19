HTTP_STATUS = {200: "OK", 400: "Bad Request"}


class ConsoleOutput:
    """A class to have fine-grained control over repeated messages in stdout"""
    def __init__(self):
        self.smart_buffer = []

    def print(self, *args):
        """print all non-duplicate args in a new line"""
        for arg in args:
            if arg.__repr__() not in self.smart_buffer:
                print(arg)
                self.smart_buffer.append(arg.__repr__())

    def flush(self):
        """empties buffer"""
        self.smart_buffer = []


class TicTacToeHTTPCommand:
    """A class to construct HTTP GET POST and response messages"""

    base_http_post = "POST HTTP/1.1\r\n" \
                     + "Host: {ip}\r\n"\
                     + "Content-Type: application/json\r\n"\
                     + "Content-Length: {con_len}\r\n\r\n"

    base_http_response = "HTTP/1.1 {status_code} {status_msg}\r\n" \
                         + "Content-Type: application/json\r\n"\
                         + "Content-Length: {con_len}\r\n\r\n"

    base_http_get = "GET / HTTP/1.1\r\n" \
                    + "Host: {ip}\r\n" \
                    + "Content-Length: {con_len}\r\n"\
                    + "Accept: application/json\r\n\r\n"

    def post_join(self, pname, ip):
        """returns post request template to join a TTT game"""
        body = '{"type": "post_join", "player_name": ' \
               + f'"{pname}"' + '}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg

    def response_join(self, sym, pid, status_code):
        """returns response template from a TTT game"""
        body = '{"type": "response_join", "id": ' \
               + str(pid) + ', "sym": ' + f'"{sym}"' + '}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_response
        headers = headers.format(
            **{"status_code": status_code,
               "status_msg": HTTP_STATUS[status_code],
               "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg

    def get_turn(self, pid, server_ip):
        """returns a get request template to get turn info from server"""
        body = '{"type": "get_turn", "player_id": ' \
               + f'"{pid}"' + '}'
        body = body.encode(encoding="utf-8")

        headers = self.base_http_get
        headers = headers.format(
            **{"ip": server_ip, "con_len": len(body)}
        ).encode(encoding="utf-8")

        http_msg = headers + body

        return http_msg

    def response_turn(self, turn_info, pid, board_state, status_code):
        """returns an HTTP response template sent after turn query"""
        body = '{"type": "response_turn", ' \
               + '"turn": "' + turn_info + '", ' \
               + '"id": "' + str(pid) + '", ' \
               + '"board_state": "' + board_state + '"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_response
        headers = headers.format(
            **{"status_code": status_code,
               "status_msg": HTTP_STATUS[status_code],
               "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg

    def post_move(self, row, col, pid, server_ip):
        """returns an HTTP POST template for sending move"""
        body = '{"type": "post_move", ' \
               + '"id": "' + str(pid) + '", ' \
               + '"row": "' + str(row) + '", ' \
               + '"col": "' + str(col) + '"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": server_ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg

    def response_move(self, desc, status_code):
        """returns a HTTP response template sent after receiving a move"""
        body = '{"type": "response_move", "desc": "' + desc + '"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_response
        headers = headers.format(
            **{"status_code": status_code,
               "status_msg": HTTP_STATUS[status_code],
               "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg

    def get_result(self, pid, server_ip):
        """returns an HTTP get template to get game result"""
        body = '{"type": "get_result", "player_id": ' \
               + f'"{pid}"' + '}'
        body = body.encode(encoding="utf-8")

        headers = self.base_http_get
        headers = headers.format(
            **{"ip": server_ip, "con_len": len(body)}
        ).encode(encoding="utf-8")

        http_msg = headers + body

        return http_msg

    def response_result(self, win_info, status_code):
        """returns an HTTP response template sent after querying response"""
        body = '{"type": "response_result", ' \
               + '"win_info": "' + str(win_info) + '"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_response
        headers = headers.format(
            **{"status_code": status_code,
               "status_msg": HTTP_STATUS[status_code],
               "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg

    def post_leave(self, pid, server_ip):
        """returns an HTTP post template to leave the game"""
        body = '{"type": "post_leave", "player_id": ' \
               + f'"{pid}"' + '}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": server_ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg

    def response_leave(self, pid, status_code):
        """returns the template response for a leave query"""
        body = '{"type": "response_leave",' \
               + '"id": ' + f'"{pid}"' + '}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_response
        headers = headers.format(
            **{"status_code": status_code,
               "status_msg": HTTP_STATUS[status_code],
               "con_len": body_len}
        ).encode(encoding="utf-8")
        http_msg = headers + body

        return http_msg
