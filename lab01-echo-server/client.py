import socket


HOST = 'localhost'
PORT = 5000
RECV_BUFFER = 1024

sock = socket.socket()

sock.connect((HOST, PORT))

print("digite [sair] para encerrar o programa")
while True:
    msg = input()
    if msg == "[sair]":
        break
    elif not msg:
        pass
    else:
        sock.send(msg.encode())
        msg = sock.recv(RECV_BUFFER)
        print(str(msg, encoding='utf-8'))

sock.close()
