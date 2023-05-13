class HTTPParser:
    def __init__(self, http_message):
        self.http_message = http_message

    def get_content(self):
        splitted_msg = self.http_message.split("\r\n\r\n")
        content = splitted_msg[-1]
        return content.strip()
