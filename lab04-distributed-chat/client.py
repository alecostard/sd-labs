import socket
import select
import sys
import datetime

from Message import Message

SERVER_HOST = ""
SERVER_PORT = 21345


def main():
    state = {'active': False}
    state["username"] = input("Digite seu nome: ")
    print("Para ajuda, digite \\ajuda")
    print("Para se conectar ao servidor, digite \\ativar")

    with socket.socket() as server_conn:
        connect_with_server(server_conn, state["username"])
        state["recipient"] = state["username"]
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
        print("Mensagem não suportada: ", msg)


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

    elif cmd == r"\ativar":
        state['active'] = True
        Message(Message.INTRODUCTION, state["username"]).send(conn)

    elif cmd == r"\inativar":
        state['active'] = False
        Message(Message.FAREWELL).send(conn)

    elif cmd.startswith(r"\para"):
        state['recipient'] = cmd.split()[1]
        print(f"conversando com {state['recipient']}")

    elif cmd == r"\lista":
        Message(Message.REQUEST_LIST).send(conn)

    elif cmd == r"\ajuda":
        print_help()

    else:
        if state["active"]:
            data = {"recipient": state["recipient"], "text": cmd}
            Message(Message.CHAT_MESSAGE, data).send(conn)
        else:
            print("Você não pode enviar mensagens enquanto estiver inativo.")


def now():
    """
    Retorna a data e hora atual como string formatada de acordo com o locale.
    """
    return datetime.datetime.now().strftime("%X")


def print_help():
    def print_cmd_description(command, description):
        print(f'{command:<20}{description}')

    print_cmd_description(r"\ativar", "tornar-se ativo")
    print_cmd_description(r"\inativar", "tornar-se inativo")
    print_cmd_description(r"\lista", "lista usuário ativos")
    print_cmd_description(r"\para x", "começa uma conversa com o usuario x")
    print_cmd_description(r"\ajuda", "exibe esta mensagem de ajuda")
    print_cmd_description(r"\fim", "sair da aplicação")


if __name__ == "__main__":
    main()
