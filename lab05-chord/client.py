from Server import Server
from Message import Message
from Node import Node
import sys
import math
import multiprocessing
import socket
import csv

HOST = "localhost"
LOCAL_PORT = 10002
ADDRESS_SERVER_PORT = 10001
NODE_START_PORT = 32000


def main():
    client = setup_client()
    client.start()


def handle_commands():  # tratador de stdin do cliente
    try:
        cmd = input()
    except EOFError:
        cmd = "sair"

    op, args = parse_cmd(cmd)

    try:
        if op == "sair":
            sys.exit()

        elif op == "busca":
            id, from_node, key = args
            port = ask_port(from_node)
            lookup(port, from_node, key, id)

        elif op == "insere":
            from_node, key, value = args
            port = ask_port(from_node)
            insert(port, from_node, key, value)

        else:
            print(f"Comando não suportado: {cmd}")
    
    except ValueError:
        print("Argumentos errados. Tente novamente")

def parse_cmd(cmd):
    """Analisa a string cmd e retorna uma tupla no format (op, args)"""
    tokens = list(csv.reader([cmd.replace('(', ',').replace(')', '')]))[0]
    tokens = [token.strip() for token in tokens]
    return tokens[0], tokens[1:]


def handle_messages(conn):  # tratador de mensagens do cliente
    msg = Message.receive(conn)

    if not msg:
        return

    elif msg.type == "LOOKUP_RESPONSE":
        body = msg.body
        print(
            f'consulta {body["query_id"]} chave: {body["key"]}: {body["value"]}')

    else:
        print(f"Recebeu mensagem não suportada: {msg}")


def ask_port(node):
    """Pergunta ao servidor de endereços a porta na qual o nó está rodando e
    retorna esse valor."""
    node = int(node)
    with socket.socket() as conn:
        conn.connect((HOST, ADDRESS_SERVER_PORT))
        Message("ADDRESS_LOOKUP", node).send(conn)
        msg = Message.receive(conn)
        return msg.body["port"]


def lookup(port, from_node, key, query_id):
    from_node = int(from_node)
    print(f"pedindo pro nó {from_node} buscar chave {key}")
    body = {"key": key, "requester": (HOST, LOCAL_PORT), "query_id": query_id}
    Message("LOOKUP_REQUEST", body).connect_and_send(HOST, port)


def insert(port, from_node, key, value):
    from_node = int(from_node)
    print(f"pedindo pro nó {from_node} inserir {value} com chave {key}")
    body = {"key": key, "value": value}
    Message("INSERT_REQUEST", body).connect_and_send(HOST, port)


def setup_client():
    client = Server(HOST, LOCAL_PORT)
    client.set_stdin_handler(handle_commands)
    client.set_msg_handler(handle_messages)
    return client


if __name__ == "__main__":
    main()
