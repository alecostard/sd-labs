import socket
import sys
import re

from Message import Message


HOST = 'localhost'
PORT = 5000
RECV_BUFFER = 1024


def main():
    with socket.socket() as s:
        s.connect((HOST, PORT))

        print("[Input a blank line to quit.]")
        while True:
            filename = input("enter file name: ")

            if filename == "":
                break

            Message("rank_words", filename).send(s)
            response = Message.receive(s)

            if response.type == "ok":
                show_words(response.contents)
            else:
                print("[ERROR]", response.contents)


def show_words(word_ranking):
    """Exibe uma tabela com o conteúdo de word_ranking."""
    print("freq\tpalavra")
    print("-" * 20)
    for [word, frequency] in word_ranking:
        print("{:>4}:\t{}".format(frequency, word))


if __name__ == "__main__":
    main()
