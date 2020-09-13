import socket
import re
import sys
import select
import multiprocessing


from Message import Message
from wordcount import top_words

HOST = ''
PORT = 5000
RECV_BUFFER = 1024


def main():
    with socket.socket() as sock:
        server_setup(sock)
        print("listening...")
        serve(sock)


def serve(sock):

    def spawn_task():
        """Cria um novo processo para servir a requisição."""
        client = multiprocessing.Process(target=server_dispatch, args=(conn,))
        clients.append(client)
        client.start()

    def wait_clients():
        """Bloqueia enquanto houver processos clientes executando."""
        if clients:
            print("waiting remaining clients...")
        for c in clients:
            c.join()

    clients = []
    while True:
        read_ready, _, _ = select.select([sock, sys.stdin], [], [])
        for ready in read_ready:
            if ready == sock:
                conn, addr = sock.accept()
                print("connected with ", addr)
                spawn_task()
            elif ready == sys.stdin:
                cmd = input()
                if cmd == "fim":
                    # desliga o socket para leitura. novas conexões serão recusadas
                    sock.shutdown(socket.SHUT_RD)
                    wait_clients()
                    return


def server_setup(s):
    """Configuração do servidor."""
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    s.setblocking(False)


def server_dispatch(conn):
    """Recebe uma mensagem e atua de acordo com seu tipo."""
    with conn:
        while True:
            message = Message.receive(conn)
            if not message:
                break
            elif message.type == "rank_words":
                message = handle_rank_words(message.contents)
                message.send(conn)
            else:
                Message("error", message.type + " not supported").send(conn)


def handle_rank_words(filename):
    """Trata a mensagem de ordenar palavras do arquivo filename."""
    # valida nome do arquivo (para evitar ataques)
    valid_filename = re.fullmatch(r'\w[\.\w]*', filename) is not None
    if not valid_filename:
        return Message("error", "invalid filename")

    # acessa a camada de processamento
    try:
        words_with_freqs = top_words(filename)
        return Message("ok", words_with_freqs)
    except FileNotFoundError:
        return Message("error", "file not found")


if __name__ == "__main__":
    main()
