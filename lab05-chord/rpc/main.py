from Node import Node

import multiprocessing
import rpyc
import math
import time


PORT_START = 32123


def main():
    node_count = ask_parameter()
    ports = initialize_ports(node_count)
    nodes = create_nodes(ports)
    try:
        start_nodes(nodes)
        interactive_loop(ports)
    finally:
        stop_nodes(nodes)


def interactive_loop(ports):
    time.sleep(0.1)
    while True:
        cmd = input("> ")
        op, args = parse_cmd(cmd)

        if op == "insere":
            starting_node, key, value = args
            insert(ports, starting_node, key, value)

        if op == "busca":
            id, starting_node, key = args
            lookup(ports, starting_node, key)

        elif op == "sair":
            return

        else:
            print(f"Comando desconhecido: {op}")


def ask_parameter():
    # n = int(input("Digite o parâmetro n: "))
    return int(2**4)


def initialize_ports(node_count):
    return [PORT_START + n for n in range(node_count)]


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


def fingers(id, ports):
    n = int(math.log2(len(ports)))
    return [ports[(id + 2**i) % 2**n] for i in range(n)]


# talvez não seja necessario para essa atividade
def predecessor(id, ports):
    return ports[id - 1]


def parse_cmd(cmd):
    tokens = cmd.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
    return tokens[0], tokens[1:]


def insert(ports, node_id, key, value):
    node_id = int(node_id)
    with rpyc.connect("localhost", ports[node_id]) as conn:
        node = conn.root
        print(node.pong())


def lookup(ports, node_id, key):
    node_id = int(node_id)
    with rpyc.connect("locahost", ports[node_id]) as conn:
        node = conn.root
        print(node.lookup(key))

if __name__ == "__main__":
    main()
