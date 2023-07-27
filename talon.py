import socket
from sty import fg, bg, ef, rs
import ipaddress
import argparse
from dotenv import dotenv_values


def print_logo():
    with open("unicode_logo.txt") as file:
        logo = file.read()
    print(f"{fg(35, 173, 245)}{logo}{rs.all}")


def charge_templates():
    global errors
    global basic
    basic = dotenv_values('basic_templates.txt')
    errors = dotenv_values('errors_templates.txt')


def parse_arguments():
    global host
    global port
    global buffer_size
    PORT_MAX_VALUE = 65535
    parser = argparse.ArgumentParser(
        prog="Talon", usage=errors['I_USAGE'].format(**globals()))
    parser.add_argument('-H', '--host', default="0.0.0.0", required=False)
    parser.add_argument('-p', '--port', type=int, default=443, required=False)
    parser.add_argument('-c', '--count', required=False,)
    parser.add_argument('-b', '--buffer-size',
                        metavar="buffer_size", type=int, default=2048)
    args = parser.parse_args()
    host = args.host
    port = args.port
    buffer_size = args.buffer_size

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


class Session:
    def __init__(self, server_host, server_port, buf_size):
        try:
            self.buf_size = buf_size
            self.l_host = server_host
            self.l_port = server_port
            self.addr = (server_host, server_port)
        except ValueError:
            print(errors['E_INVALID_IP'].format(**globals()))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        try:
            self.connect()
            self.recvData()
            self.sock.close()

        except socket.error as err:
            print(errors['E_CUSTOM'].format(**globals()))

    def connect(self):
        self.sock.bind(self.addr)
        self.sock.listen(5)
        self.conn, self.r_addr = self.sock.accept()

    def recvData(self):
        try:
            i = 0
            while True:
                result = b""
                self.buffer = ""
                self.buffer = self.conn.recv(self.buf_size)
                print("LINEA", i)
                while len(self.buffer) and chr(self.buffer[-1]) != '\n':
                    print()
                    result += self.buffer
                    self.buffer = self.conn.recv(self.buf_size)
                    print("Resultado", result)
                i += 1
                if len(self.buffer) == 0:
                    break
            print("DATA: ", result)
        except socket.error as err:
            print(errors['E_CUSTOM'].format(**globals()))

    # def sendData(self):


if __name__ == "__main__":
    charge_templates()
    parse_arguments()
    print_logo()
    addr_info = socket.getaddrinfo(host, port, type=socket.AF_INET)[0]
    session = Session(host, port, buffer_size)
    print(basic['B_START_SES'].format(**globals()))
    session.start()
