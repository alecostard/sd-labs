import socket
import re
import sys
import select


from Message import Message
from wordcount import top_words

HOST = ''
PORT = 5000
RECV_BUFFER = 1024


def main():
    with socket.socket() as sock:
        server_setup(sock)
        print("listening...")
        while True:
            read_ready, _, _ = select.select([sock, sys.stdin], [], [])
            for ready in read_ready:
                if ready == sock:
                    conn, addr = sock.accept()
                    with conn:
                        print("connected with ", addr)
                        server_dispatch_loop(conn)
                elif ready == sys.stdin:
                    cmd = input()
                    if cmd == "fim":
                        return


def server_setup(s):
    """Configuração do servidor."""
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    s.setblocking(False)


def server_dispatch_loop(conn):
    """Recebe uma mensagem e atua de acordo com seu tipo."""
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
