import socket


HOST = ''
PORT = 5000
RECV_BUFFER = 1024

with socket.socket() as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)

    conn, address = sock.accept()
    with conn:
        while True:
            msg = conn.recv(RECV_BUFFER)

            if not msg:
                break
            else:
                conn.sendall(msg)
