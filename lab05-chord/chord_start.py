from Server import Server
from Message import Message
from Node import Node
import sys
import math
import multiprocessing
import socket
import csv

HOST = "localhost"
PORT = 10001
NODE_START_PORT = 32000


def main():
    n = int(input("Digite o parâmetro n: "))
    node_count = 2 ** n
    ports = [NODE_START_PORT + n for n in range(node_count)]
    nodes = create_nodes(ports)
    address_server = setup_server(ports)

    try:
        start_nodes(nodes)
        address_server.start()
    finally:
        stop_nodes(nodes)


def handle_messages(conn):  # tratador de mensagens do servidor de endereços.
    msg = Message.receive(conn)

    if msg.type == "ADDRESS_LOOKUP":
        target = msg.body
        body = {"host": HOST, "port": NODE_START_PORT + target}
        Message("ADDRESS_RESPONSE", body).send(conn)

    else:
        print(f"Recebeu mensagem não suportada: {msg}")


def setup_server(ports):
    server = Server(HOST, PORT)
    server.set_msg_handler(handle_messages)
    return server


def fingers(id, ports):
    """Retorna a finger table para o host identificado por id."""
    n = int(math.log2(len(ports)))
    return [ports[(id + 2**i) % 2**n] for i in range(n)]


def create_nodes(ports):
    nodes = []
    for id in range(len(ports)):
        port = ports[id]
        node = Node(id, port, fingers(id, ports))
        nodes.append(multiprocessing.Process(target=node.run))

    return nodes


def start_nodes(nodes):
    for node in nodes:
        node.start()


def stop_nodes(nodes):
    for node in nodes:
        node.terminate()
        node.join()


if __name__ == "__main__":
    main()
