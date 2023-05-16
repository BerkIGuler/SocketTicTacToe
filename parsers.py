from argparse import ArgumentParser
import json


class HTTPParser:
    def __init__(self, http_message):
        if isinstance(http_message, bytes):
            try:
                self.http_message = http_message.decode(encoding="utf-8")
            except Exception as e:
                raise e
        elif isinstance(http_message, str):
            self.http_message = http_message

        else:
            raise TypeError(
                f"http_message must either be of type bytes or str not {type(http_message)}"
            )

    def get_content(self):
        try:
            header, content = self.http_message.split("\r\n\r\n")
        except ValueError:
            content = None
        else:
            content = content.strip()

        return content

    def get_json_content(self):
        try:
            header, content = self.http_message.split("\r\n\r\n")
        except ValueError:
            content = None

        if content:
            return json.loads(content)

    def check_content_len(self):
        content_len = self._get_header_val(search_key="Content-Length")
        content = self.get_content()

        match = False
        if content_len and (int(content_len) == len(content.encode("utf-8"))):
            match = True

        return match

    def _get_header_val(self, search_key):
        try:
            headers, content  = self.http_message.split("\r\n\r\n")
        except ValueError:
            headers = self.http_message.split("\r\n")
        else:
            headers = headers.split("\r\n")

        val = None

        for header in headers:
            if search_key in header:
                colon_pos = header.find(":")
                # assume one space after :, i.e. search_key: val
                val = header[colon_pos + 2:]
                return val

        return val


def parse_port():
    """return port parsed from cli"""
    parser = ArgumentParser(
        description="Parses port number for tic-tac-toe server"
    )

    parser.add_argument("port",
                        type=int,
                        help="port number for tic-tac-toe server")

    args = parser.parse_args()
    return args.port


