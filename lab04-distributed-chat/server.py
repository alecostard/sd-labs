import socket
import select
import sys
from Message import Message

HOST = ''
PORT = 21345


def main():
    with socket.socket() as sock:
        server_setup(sock)
        server_loop(sock)


def server_setup(sock):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    sock.setblocking(False)


def server_loop(sock):
    connected_users = {}
    while True:
        read_list = [sys.stdin, sock] + list(connected_users.keys())
        read, _, _ = select.select(read_list, [], [])
        for ready in read:
            if ready == sock:
                handle_new_user(ready, connected_users)
            elif ready == sys.stdin:
                try:
                    cmd = input()
                except EOFError:
                    return
                if cmd == r"\fim":
                    close_all_sockets(connected_users)
                    return
                elif cmd == r"\clientes":
                    for c, name in connected_users.items():
                        print(f'{name}: {c}')
            elif ready in connected_users:
                handle_message(ready, connected_users)


def handle_new_user(sock, connected_users):
    """
    Cria uma conexão com um novo usuário e adiciona no mapa de conexões.
    """
    conn, _ = sock.accept()
    conn.setblocking(False)
    connected_users[conn] = None


def close_all_sockets(connected_users):
    for conn in connected_users:
        conn.close()


def handle_message(conn, connected_users):
    """
    Recebe uma mensagem e reage de acordo com o seu tipo.
    """
    msg = Message.receive(conn)

    if not msg:
        username = connected_users[conn]
        conn.close()
        del connected_users[conn]
        broadcast(connected_users, Message(Message.USER_LEFT, username))

    elif msg.type == Message.INTRODUCTION:
        username = msg.contents
        broadcast(connected_users, Message(Message.NEW_USER, username))
        connected_users[conn] = username
        usernames = [u for u in connected_users.values() if u is not None]
        Message(Message.LIST_USERS, usernames).send(conn)

    elif msg.type == Message.FAREWELL:
        username = connected_users[conn]
        connected_users[conn] = None
        broadcast(connected_users, Message(Message.USER_LEFT, username))

    elif msg.type == Message.REQUEST_LIST:
        usernames = [u for u in connected_users.values() if u is not None]
        Message(Message.LIST_USERS, usernames).send(conn)

    elif msg.type == Message.CHAT_MESSAGE:
        recipient = msg.contents["recipient"]
        sender = connected_users[conn]
        recipient_conn = [
            c for c, n in connected_users.items() if n == recipient
        ]
        if recipient_conn:
            contents = {"text": msg.contents["text"], "sender": sender}
            Message(Message.CHAT_MESSAGE, contents).send(recipient_conn[0])
        else:
            Message(Message.RECIPIENT_NOT_FOUND, recipient).send(conn)


def broadcast(clients, message):
    """
    Envia uma mensagem para todos os clientes conectados.
    """
    for (conn, name) in clients.items():
        if name:
            message.send(conn)


if __name__ == "__main__":
    main()
