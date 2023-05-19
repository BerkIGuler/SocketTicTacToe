HTTP_STATUS = {200: "OK", 400: "Bad Request"}


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
                    + "Accept: application/json\r\n\r\n"

    def join_request(self, p_name, ip):
        """join post request template to server"""
        body = '{"type": "join", "player_name": ' \
               + f'"{p_name}"' + '}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request

    def symbol_and_id(self, sym, p_id):
        """sym and id response template from server"""
        body = '{"type": "join", "player_id": ' \
               + str(p_id) + ', "player_sym": ' + f'"{sym}"' + '}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_response
        headers = headers.format(
            **{"status_code": 200, "status_msg": "OK", "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request

    def turn(self, ip, id, sym, board_state, your_turn=False):
        """turn post request from the server"""
        if your_turn:
            turn_info = "your_turn"
        else:
            turn_info = "wait_turn"

        body = '{"type": "' + turn_info + '", ' \
               + '"id": "' + str(id) + '", ' \
               + '"sym": "' + sym + '", ' \
               + '"board_state": "' + board_state + '"}' \

        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request

    def move(self, row, col, p_id, ip):
        """move post request to server"""
        body = '{"type": "move", ' \
               + '"id": "' + str(p_id) + '", ' \
               + '"row": "' + str(row) + '", ' \
               + '"col": "' + str(col) + '"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request

    def status_request(self, ip):
        """status post request to server"""
        body = '{"type": "status"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request

    def validate_move(self, description, status_code):
        """valid/invalid move response from server"""
        body = '{"type": "move_status", "desc": "' + description + '"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_response
        headers = headers.format(
            **{"status_code": status_code,
               "status_msg": HTTP_STATUS[status_code],
               "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request

    def result(self, win_info, ip):
        """result post request from the server"""
        body = '{"type": "result", ' \
               + '"win_info": "' + str(win_info) + '"}'
        body = body.encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request




