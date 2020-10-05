import json

RECV_BUFFER = 64
MESSAGE_BYTE_SIZE = 4


class Message:
    INTRODUCTION = "introduction"
    NEW_USER = "new_user"
    LIST_USERS = "list_users"
    REQUEST_LIST = "request_list"
    USER_LEFT = "user_left"
    CHAT_MESSAGE = "chat_message"
    RECIPIENT_NOT_FOUND = "recipient_not_found"

    def __init__(self, msgtype, contents=""):
        self.type = msgtype
        self.contents = contents

    def tojson(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.tojson()

    def send(self, conn):
        msg = self.tojson()
        size = len(msg).to_bytes(MESSAGE_BYTE_SIZE, "big")
        conn.sendall(size + str.encode(msg))

    @staticmethod
    def receive(conn):
        size = conn.recv(MESSAGE_BYTE_SIZE)
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
        return Message(message["type"], message["contents"])
