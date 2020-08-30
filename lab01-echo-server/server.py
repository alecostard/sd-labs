import socket


HOST = ''
PORT = 5000
RECV_BUFFER = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind((HOST, PORT))
sock.listen(1)
conn, address = sock.accept()

while True:
    msg = conn.recv(RECV_BUFFER)

    if not msg:
        break
    else:
        conn.sendall(msg)

conn.close()
sock.close()
