import socket
import subprocess
import random

# Inicializar socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Asignar puerto aleatorio entre 1000 y 2000
port = random.randint(1000,2000)

# Asignar direccion IP
s.bind(('', port))

# Poner el socket a la escucha
s.listen(5)

print("Esperando conexion en el puerto:", port)

# Aceptar conexiones entrantes
conn, addr = s.accept()

print("Conexion establecida desde:", addr)

# Ejecutar comando "ssh-keygen -t rsa -f id_rsa -N "" " para generar una clave ssh
output = subprocess.run(["ssh-keygen", "-t", "rsa", "-f", "id_rsa", "-N", ""], capture_output=True, text=True)

# Enviar al cliente la clave publica
with open("id_rsa.pub", "r") as pubkey:
    pubkey_content = pubkey.read()
    conn.send(pubkey_content.encode())

# Mostrar al cliente la clave privada
with open("id_rsa", "r") as privkey:
    privkey_content = privkey.read()
    conn.send(privkey_content.encode())

# Cerrar conexion
conn.close()

#liberar el puerto
s.shutdown(socket.SHUT_RDWR)
s.close()
