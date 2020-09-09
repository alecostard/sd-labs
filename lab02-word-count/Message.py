import json

RECV_BUFFER = 1024

class Message:
    def __init__(self, msgtype, contents):
        self.type = msgtype
        self.contents = contents

    def tojson(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.tojson()

    def send(self, conn):
        conn.sendall(str.encode(self.tojson()))

    @staticmethod
    def receive(conn):
        message = json.loads(conn.recv(RECV_BUFFER).decode())
        return Message(message["type"], message["contents"])
