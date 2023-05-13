

class TicTacToeHTTPCommand:
    join_request_body = {
        "type": "",
        "player_name": "",
    }

    base_http_post = "POST HTTP/1.1\r\n" \
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
        body = str(body).encode(encoding="utf-8")
        body_len = len(body)

        headers = self.base_http_post
        headers = headers.format(
            **{"ip": ip, "con_len": body_len}
        ).encode(encoding="utf-8")
        http_request = headers + body

        return http_request
