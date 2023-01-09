import socket
import sys

host = '127.0.0.1'
port = 4444
BUFFER_SIZE = 1024
MESSAGE = 'Hola, mundo!'
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_tcp:
    socket_tcp.connect((host, port))
    # Convertimos str a bytes
    socket_tcp.send(MESSAGE.encode('utf-8'))
    data = socket_tcp.recv(BUFFER_SIZE)
    print(data.decode('utf-8'))
