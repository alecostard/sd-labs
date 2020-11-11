import json
import socket

RECV_BUFFER = 64
MESSAGE_BYTE_SIZE = 4
LOG = False

class Message:
    def __init__(self, msgtype, body=""):
        self.type = msgtype
        self.body = body

    def tojson(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.tojson()

    def send(self, conn):
        log(f"Sending message {self.type}")
        msg = self.tojson()
        size = len(msg).to_bytes(MESSAGE_BYTE_SIZE, "big")
        conn.sendall(size + str.encode(msg))

    def connect_and_send(self, host, port):
        with socket.socket() as conn:
            conn.connect((host, port))
            self.send(conn)        

    @staticmethod
    def receive(conn):
        size = b''
        for _ in range(MESSAGE_BYTE_SIZE):
            size += conn.recv(1)
            if not size:
                return None
        size = int.from_bytes(size, "big")

        received = 0
        raw = b''
        while received < size:
            to_receive = min(RECV_BUFFER, size - received)
            received += RECV_BUFFER
            raw += conn.recv(to_receive)

        message = json.loads(raw.decode())
        log(f"Received message {message['type']}")
        return Message(message["type"], message["body"])

def log(msg):
    if LOG:
        print(msg)