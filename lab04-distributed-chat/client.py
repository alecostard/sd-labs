import socket
import select
import sys
import datetime

from Message import Message

SERVER_HOST = ""
SERVER_PORT = 21345


def main():
    username = input("Digite seu nome: ")
    print("Para ajuda, digite \\ajuda")

    with socket.socket() as server_conn:
        connect_with_server(server_conn, username)
        state = {"recipient": username}
        print(f"conversando com {state['recipient']}")
        while True:
            read_ready, _, _ = select.select([sys.stdin, server_conn], [], [])

            for ready in read_ready:
                if ready == server_conn:
                    handle_message(server_conn)

                elif ready == sys.stdin:
                    handle_commands(server_conn, state)


def connect_with_server(server_conn, username):
    server_conn.connect((SERVER_HOST, SERVER_PORT))
    server_conn.setblocking(False)
    Message(Message.INTRODUCTION, username).send(server_conn)


def handle_message(conn):
    """
    Recebe uma mensagem e reage de acordo com o seu tipo.
    """
    msg = Message.receive(conn)

    if not msg:
        print("Servidor se desconectou")
        conn.close()
        sys.exit()

    elif msg.type == Message.NEW_USER:
        print(f"[Usuário {msg.contents} se conectou]")

    elif msg.type == Message.USER_LEFT:
        print(f"[Usuário {msg.contents} se desconectou]")

    elif msg.type == Message.LIST_USERS:
        print("-" * 20)
        userlist = msg.contents
        print("Usuários ativos")
        print("-" * 20)
        for username in userlist:
            print(f'{username:>20}')
        print("-" * 20)

    elif msg.type == Message.CHAT_MESSAGE:
        print(f'[{now()} - {msg.contents["sender"]}]: {msg.contents["text"]}')

    elif msg.type == Message.RECIPIENT_NOT_FOUND:
        print(f"Usuário {msg.contents} não está ativo.")

    else:
        print(msg)


def handle_commands(conn, state):
    """
    Lê comandos da entrada padrão e reage de acordo.
    """
    try:
        cmd = input()
    except EOFError:
        sys.exit()

    if cmd == r"\fim":
        sys.exit()

    elif cmd.startswith(r"\para"):
        state['recipient'] = cmd.split()[1]
        print(f"conversando com {state['recipient']}")

    elif cmd == r"\lista":
        Message(Message.REQUEST_LIST).send(conn)

    elif cmd == r"\ajuda":
        print_help()

    else:
        data = {"recipient": state['recipient'], "text": cmd}
        Message(Message.CHAT_MESSAGE, data).send(conn)


def now():
    """
    Retorna a data e hora atual como string formatada de acordo com o locale.
    """
    return datetime.datetime.now().strftime("%X")


def print_help():
    print("\\ajuda\t\tmostra essa mensagem de ajuda")
    print("\\lista\t\tlista usuários ativos")
    print("\\para x\t\tcomeça uma conversa com o usuario x")
    print("\\fim\t\tsair da aplicação")


if __name__ == "__main__":
    main()
