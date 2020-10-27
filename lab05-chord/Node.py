from Server import Server
from Message import Message
import socket

HOST = "localhost"


class Node:
    """
    Nó em uma rede 'Chord' completa e imutável.
    """
    def __init__(self, id, port, fingers):
        self.id = id
        self.fingers = fingers
        self.storage = {}
        self.server = Server(HOST, port)

    def setup(self):
        """Configura o servidor, instalando um tratador de mensagems."""
        self.server.set_msg_handler(self.make_message_handler())

    def run(self):
        print(f"nó {self.id} iniciando")
        self.setup()
        self.server.start()

    def make_message_handler(self):
        """Retorna uma rotina de tratamento de mensagens."""
        def handle_message(conn):
            msg = Message.receive(conn)

            if not msg:
                return

            elif msg.type == "LOOKUP_REQUEST":
                print(f"{self.id} recebeu requisição de busca")
                body = msg.body
                self.lookup(body["key"], body["requester"], body["query_id"])

            elif msg.type == "INSERT_REQUEST":
                print(f"{self.id} recebeu requisição de inserção")
                self.insert(msg.body["key"], msg.body["value"])

            else:
                print(f"Recebeu mensagem não suportada: {msg}")                

        return handle_message

    def lookup(self, key, requester, query_id):
        target = self.target_node(key)

        if target == self.id:
            host, port = requester
            body = {"key": key, "value": self.storage.get(key), "query_id": query_id}
            Message("LOOKUP_RESPONSE", body).connect_and_send(host, port)

        else:
            closest = self.closest_predecessor(target)
            port = self.fingers[closest]
            body = {"key": key, "requester": requester, "query_id": query_id}
            Message("LOOKUP_REQUEST", body).connect_and_send(HOST, port)

    def insert(self, key, value):
        target = self.target_node(key)

        if target == self.id:
            print(f"guardando {value} na chave {key} do nó {self.id}")
            self.storage[key] = value

        else:
            closest = self.closest_predecessor(target)
            port = self.fingers[closest]
            body = {"key": key, "value": value}
            Message("INSERT_REQUEST", body).connect_and_send(HOST, port)

    def network_size(self):
        return 2 ** len(self.fingers)

    def target_node(self, key):
        return hash(key) % self.network_size()

    def closest_predecessor(self, id):
        n = self.network_size()
        for k in reversed(range(len(self.fingers))):
            low = 2 ** k
            high = 2 * low
            if id in [(self.id + i) % n for i in range(low, high)]:
                return k
