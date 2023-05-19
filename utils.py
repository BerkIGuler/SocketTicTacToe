HTTP_STATUS = {200: "OK", 400: "Bad Request"}


class ConsoleOutput:
    def __init__(self):
        self.smart_buffer = []

    def print(self, *args):
        for arg in args:
            if arg.__repr__() not in self.smart_buffer:
                print(arg)
                self.smart_buffer.append(arg.__repr__())

    def flush(self):
        self.smart_buffer = []


class TicTacToeHTTPCommand:

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
        """join post request template to server"""
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
