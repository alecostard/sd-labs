import socket
import select
import sys


class Server:
    """
    Servidor básico que escuta tanto conexões no endereço e porta passados para
    o __init__ quanto a entrada padrão, caso o tratador seja instalado. 
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connections = []
        self.msg_handler = None
        self.stdin_handler = None

    def __del__(self):
        if self.socket:
            self.socket.close()

    def start(self):
        self.setup()
        self.run()

    def setup(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.socket.setblocking(False)

    def run(self):
        while True:
            read, _, _ = select.select(self.readlist(), [], [])
            for ready in read:
                if ready == self.socket:
                    conn, _ = self.socket.accept()
                    conn.setblocking(False)
                    self.connections.append(conn)

                elif ready in self.connections:
                    self.msg_handler(ready)
                    ready.close()
                    self.connections.remove(ready)

                elif ready == sys.stdin:
                    self.stdin_handler()

    def readlist(self):
        if self.stdin_handler:
            return [self.socket, sys.stdin] + self.connections
        else:
            return [self.socket] + self.connections

    # setters para instalação de tratadores de mensagem e stdin
    def set_msg_handler(self, handler):
        self.msg_handler = handler

    def set_stdin_handler(self, handler):
        self.stdin_handler = handler
