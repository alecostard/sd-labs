import rpyc

from rpyc.utils.server import ThreadedServer


class Node(rpyc.Service):
    def __init__(self, id, port, fingers):
        self.port = port
        self.id = id
        self.fingers = fingers

    def on_connect(self, conn):
        print(f"node {self.id} conected")

    def on_disconnect(self, conn):
        print(f"node {self.id} disconnected")

    def run(self):
        print(f"iniciando nó {self.id} na porta {self.port}")
        self.server = ThreadedServer(self, port=self.port)
        self.server.start()

    def exposed_lookup(self, key):
        target = self.target_node(key)

        if target == self.id:
            print(self.id)

        else:
            closest = self.closest_predecessor(target)
            with rpyc.connect("localhost", self.fingers[closest]) as conn:
                node = conn.root
                node.lookup(key)

    def target_node(self, key):
        return hash(key) % self.network_size()

    def network_size(self):
        return 2 ** len(self.fingers)

    def closest_predecessor(self, id):
        n = self.network_size()
        for k in reversed(range(len(self.fingers))):
            low = 2 ** k
            high = 2 * low
            if id in [(self.id + i) % n for i in range(low, high)]:
                return k


