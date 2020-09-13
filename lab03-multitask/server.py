import socket
import json
import re

from Message import Message
from wordcount import top_words

HOST = ''
PORT = 5000
RECV_BUFFER = 1024


def main():
    with socket.socket() as s:
        # opções para poder reusar uma porta logo após o encerramento do programa
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)     # 1 para conectar apenas com 1 cliente por vez
        print("listening...")
        connect_loop(s)


def connect_loop(socket):
    """Coloca o servidor em um loop, sempre que uma conexão é encerrada,
     ele espera outra."""
    while True:
        conn, addr = socket.accept()
        with conn:
            print("connected with ", addr)
            server_dispatch_loop(conn)


def server_dispatch_loop(conn):
    """Recebe uma mensagem e atua de acordo com seu tipo."""
    while True:
        message = Message.receive(conn)
        if message.type == "end_connection":
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
