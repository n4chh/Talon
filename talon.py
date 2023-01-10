import socket
from sty import fg, bg, ef, rs
import ipaddress
import argparse
from dotenv import load_dotenv, dotenv_values


def print_logo():
    with open("unicode_logo.txt") as file:
        logo = file.read()
    print(f"{fg(35, 173, 245)}{logo}{rs.all}")


def charge_templates():
    global errors
    load_dotenv()
    errors = dotenv_values('errors_templates.txt')


def parse_arguments():
    global host
    global port
    PORT_MAX_VALUE = 65535
    parser = argparse.ArgumentParser(prog="Talon", usage=errors['I_USAGE'].format(**globals()))
    parser.add_argument('host')
    parser.add_argument('port', type=int,)
    parser.add_argument('-c', '--count', required=False, )
    args = parser.parse_args()
    host = args.host
    port = args.port
    lhost = ipaddress.ip_address(args.host)
    if not lhost.is_private:
        print(errors['W_PUBLIC_IP'].format(**globals()))
        exit()
    if args.port > PORT_MAX_VALUE or args.port < 0:
        print(errors['E_INVALID_PORT'].format(**globals()))
        exit()


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
