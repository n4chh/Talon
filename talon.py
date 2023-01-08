import socket

host = socket.gethostname()
port = 10042
BUFFER_SIZE = 1024

session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
session.bind((host, port))
session.listen(5)
conn, remote_addr = session.accept()
with conn:
    while True:
        print("Conexion establecida con:", remote_addr)
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break    
        else:
            print("Datos recibidos", data.decode('utf-8'))
        conn.send(data)
