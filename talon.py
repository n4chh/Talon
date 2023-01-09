import socket
from colored import fg, bg, attr
import ipaddress
import argparse

PORT_MAX_VALUE = 65535
host = '0.0.0.0'
port = 4444


def parse_arguments():
    global host
    global port
    parser = argparse.ArgumentParser(prog="Talon")
    parser.add_argument('host')
    parser.add_argument('port', type=int,)
    parser.add_argument('-c', '--count', required=False, )
    args = parser.parse_args()
    print(args)
    try:
        lhost = ipaddress.ip_address(args.host)
        if not lhost.is_private:
            print(f"{bg('yellow_1')}{fg('red_3a')} Warning! {attr(0)} This IP Address is not a private one")
            exit()
        if args.port > PORT_MAX_VALUE or args.port < 0:
            print(f"{fg('red')} ERROR: {attr(0)}This is a not valid port")
            exit()
    except ValueError:
        print(f"""{fg('red')} ERROR: {attr(0)}Invalid input. Example:
python3 talon.py {fg('grey_19')}{bg('gold_3b')} host {attr(0)} {fg('grey_19')}{bg('cornflower_blue')} port {attr(0)}""")
        exit()
    

parse_arguments()
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
