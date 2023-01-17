import socket
from sty import fg, bg, ef, rs
import ipaddress
import argparse
from dotenv import dotenv_values
import pyotp


def print_logo():
    with open("unicode_logo.txt") as file:
        logo = file.read()
    print(f"{fg(35, 173, 245)}{logo}{rs.all}")


def charge_templates():
    global errors
    errors = dotenv_values('errors_templates.txt')


def parse_arguments():
    global host
    global port
    PORT_MAX_VALUE = 65535
    parser = argparse.ArgumentParser(prog="Talon", usage=errors['I_USAGE'].format(**globals()))
    parser.add_argument('host')
    parser.add_argument('port', type=int,)
    parser.add_argument('-c', '--count', required=False,)
    args = parser.parse_args()
    host = args.host
    port = args.port
    try:
        lhost = ipaddress.ip_address(args.host)
    except ValueError:
        print(errors['E_INVALID_IP'].format(**globals()))
        exit()
    if not lhost.is_private:
        print(errors['W_PUBLIC_IP'].format(**globals()))
        exit()
    if args.port > PORT_MAX_VALUE or args.port < 0:
        print(errors['E_INVALID_PORT'].format(**globals()))
        exit()


class session:
    def __init__(self, server_host, server_port):
        try:
            self.l_host = ipaddress.IPv4Address(server_host)
            self.l_port = server_port
        except ValueError:
            print(errors['E_INVALID_IP'].format(**globals()))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = 424242#Aqui vamos a usar para cifrar esto un Diffie Helman (DHP)

    def connect(self):
        self.sock.bind((self.l_host, self.l_port))
        self.sock.listen(1)
        self.conn, self.r_addr = self.sock.accept()


charge_templates()
parse_arguments()
print(host, port)
print_logo()
addr_info = socket.getaddrinfo(host, port, type=socket.AF_INET)[0]
BUFFER_SIZE = 1024

session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
session.bind(addr_info[-1])
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
