

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

