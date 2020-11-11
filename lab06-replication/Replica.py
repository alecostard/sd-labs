import sys
from threading import Timer
from Server import Server
from Message import Message

HOST = "localhost"
PORT = 32000


class Replica:
    def __init__(self, id, npeers):
        self.id = id
        self.history = []
        self.storage = 0
        self.npeers = npeers
        self.server = Server(HOST, PORT + id)
        self.writing = False
        self.acks = 0
        self.primary = 1
        self.pending_requester = None
        self.lost_race = False

    def start(self):
        self.server.set_stdin_handler(self.make_stdin_handler())
        self.server.set_msg_handler(self.make_message_handler())
        self.server.start()

    def broadcast(self, msg):
        peers = [32000 + i for i in range(1, self.npeers + 1) if i != self.id]
        for peer in peers:
            msg.connect_and_send(HOST, peer)

    def set_new_value(self, val):
        """Altera o valor guardado e adiciona no histórico."""
        self.storage = val
        self.history.append((self.id, self.storage))

    def handle_commands(self):
        try:
            cmd = input().strip()
        except EOFError:
            cmd = "fim"

        if cmd == "":
            pass

        elif cmd == "ajuda" or cmd == "?":
            Replica.print_help()

        elif cmd == "valor":
            print(f"{self.storage}")

        elif cmd == "historico":
            for id, value in self.history:
                print(f"{id} alterou para {value}")

        elif cmd == "escreve":
            if self.is_primary():
                self.enter_write_mode()
            else:
                print("Aguardando permissão para escrita.")
                self.request_token()

        elif cmd == "fim":
            sys.exit()

        else:
            print(f"Comando não reconhecido: {cmd}")

    def handle_writes(self):
        try:
            raw = input().strip()
            if raw == "pronto":
                self.exit_write_mode()
            else:
                val = int(raw)
                self.set_new_value(val)
                self.prompt_new_value()
        except ValueError:
            print(f"Valor não reconhecido: {raw}")
        except EOFError:
            self.exit_write_mode()

    def make_stdin_handler(self):
        """Tratador de stdin. Alterna entre modo de escrita e comandos."""
        def handle_stdin():
            if not self.writing:
                self.handle_commands()
            else:
                self.handle_writes()

        return handle_stdin

    def make_message_handler(self):
        def handle_message(conn):
            msg = Message.receive(conn)

            if not msg:
                return

            elif msg.type == "NEW_VALUE":
                self.storage = msg.body['value']
                port = PORT + msg.body['sender']
                Message("ACK_NEW_VALUE").connect_and_send(HOST, port)
                self.history.append((msg.body['sender'], self.storage))

            elif msg.type == "ACK_NEW_VALUE":
                # conta os acks recebidos
                self.acks += 1

                # caso tenha recebido todos, trata a requisição pendente
                if self.acks == self.npeers - 1:
                    print("Confirmações recebidas")
                    self.writing = False
                    self.acks = 0
                    self.handle_pending_request()

            # Caso seja a primária e não esteja escrevendo, envia o token.
            # Caso seja a primária e esteja escrevendo, envia o token para
            # o emissor da primeira e avisa para os demais que o token já foi
            # eviado para outro.
            # Caso não seja primária, avisa o emissor. Nesse caso é iniciado um
            # fluxo de mensagens para que o emissor descubra a primária.
            elif msg.type == "REQUEST_TOKEN":
                sender_port = PORT + msg.body

                if not self.is_primary:
                    Message("NOT_PRIMARY").connect_and_send(HOST, sender_port)
                elif not self.writing:
                    self.send_token(msg.body)
                elif not self.pending_requester:
                    self.pending_requester = msg.body
                else:
                    Message("TOKEN_TAKEN").connect_and_send(HOST, sender_port)

            elif msg.type == "TOKEN":
                self.primary = self.id
                self.enter_write_mode()
                self.broadcast(Message("NEW_PRIMARY", self.id))

            elif msg.type == "NEW_PRIMARY":
                self.primary = msg.body
                if self.lost_race:
                    self.request_token()

            # Quando outro par consegue o token antes, deixa essa falha na
            # requisição de token marcada para requisitar o token novamente
            # quando uma nova primária for anunciada.
            elif msg.type == "TOKEN_TAKEN":
                self.lost_race = True

            # Se a réplica atual pediu o token para um par que não é a primária
            # ela faz um broadcast perguntando. Apenas a primária responde.
            elif msg.type == "NOT_PRIMARY":
                self.broadcast(Message("WHO_IS_PRIMARY", self.id))

            elif msg.type == "WHO_IS_PRIMARY":
                if self.is_primary():
                    Message("AM_PRIMARY", self.id).connect_and_send(
                        HOST, msg.body)

            elif msg.type == "AM_PRIMARY":
                self.primary = msg.body
                self.request_token()

            else:
                print(f"Received message: {msg.type}")

        return handle_message

    def is_primary(self):
        return self.primary == self.id

    def prompt_new_value(self):
        print("novo valor: ", end='')
        sys.stdout.flush()

    def enter_write_mode(self):
        self.writing = True
        print("Entrando no modo de escrita. Digite 'pronto' para sair.")
        self.prompt_new_value()

    def exit_write_mode(self):
        print("Saindo do modo de escrita")
        body = {"sender": self.id, "value": self.storage}
        self.broadcast(Message("NEW_VALUE", body))
        print("Experando confirmação dos pares")

    def request_token(self):
        self.lost_race = False
        port = PORT + self.primary
        Message("REQUEST_TOKEN", self.id).connect_and_send(HOST, port)

    def send_token(self, peer):
        self.primary = None
        Message("TOKEN").connect_and_send(HOST, PORT + peer)

    def handle_pending_request(self):
        if self.pending_requester:
            self.send_token(self.pending_requester)
            self.pending_requester = False

    @staticmethod
    def print_help():
        print("comandos disponíveis:")
        print(f"{'ajuda':12}imprime essa lista de comandos")
        print(f"{'?':12}imprime essa lista de comandos")
        print(f"{'fim':12}termina a execução")
        print(f"{'valor':12}mostra o valor atual de x")
        print(f"{'escreve':12}entra no modo de escrita de x")
        print(f"{'historico':12}mostra historico de alterações de x")
