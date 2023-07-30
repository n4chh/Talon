import socket
import json
from sty import fg, bg, ef, rs
import ipaddress
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
import argparse
import fcntl
import select
import os
import sys
from dotenv import dotenv_values


def print_logo():
    with open("unicode_logo.txt") as file:
        logo = file.read()
    print(f"{fg(35, 173, 245)}{logo}{rs.all}")

# def binwrite(s, data):
#     """write bytes to stream"""
#     if hasattr(s, "mode") and "b" in s.mode:
#       return s.write(data)
#     elif hasattr(s, "buffer"):
#       return s.buffer.write(data)
#     else:
#       return s.write(b2s(data))      
    
def charge_templates():
    global errors
    global basic
    basic = dotenv_values('basic_templates.txt')
    errors = dotenv_values('errors_templates.txt')

def set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

def parse_arguments():
    global host
    global port
    global buffer_size
    global quiet
    PORT_MAX_VALUE = 65535
    parser = argparse.ArgumentParser(
        prog="Talon", usage=errors['I_USAGE'].format(**globals()))
    parser.add_argument('-H', '--host', default="0.0.0.0", required=False)
    parser.add_argument('-p', '--port', type=int, default=443, required=False)
    parser.add_argument('-c', '--count', required=False,)
    parser.add_argument('-b', '--buffer-size',
                        metavar="buffer_size", type=int, default=1024)
    parser.add_argument('-q', '--quiet', required=False)
    args = parser.parse_args()
    quiet = args.quiet
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
        # try:
        self.buf_size = buf_size
        self.l_host = server_host
        self.l_port = server_port
        self.addr = (server_host, server_port)
        self.ps = PromptSession()
        self.cmd = None
        # except ValueError:
        # print(errors['E_INVALID_IP'].format(**globals()))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def kill(self):
        self.socket.close()

    def start(self):
        try:
            self.connect()
            # self.handle_io_rev_shell()
            set_nonblocking(sys.stdout)
            self.handle_io()
                
            self.socket.close()
            print(basic['B_END_SES'].format(**globals()))
        except socket.error as err:
            print(errors['E_CUSTOM'].format(**globals()), err)

    def handle_io_rev_shell(self):
        self.status = True
        end_of_rev = "}shell finished EOF{"
        # set_nonblocking(sys.stdin)
        
        while self.status: 
            sin = [self.conn, sys.stdin]  
            rs, _, _, = select.select(sin, [], [])
            if self.conn in rs:
                self.recv_data(EOF=end_of_rev)
            if sys.stdin in rs:
                # self.cmd = input()
                self.cmd = sys.stdin.read(1080)
                self.send_data()
        # while True:
        #     self.recv_data()
        #     print("hola")
        #     print("metoca")
        #     self.send_data()
        #     print("enviado")
    
    def handle_io(self):
        while True:
            self.prompt()
            if self.cmd:
                if self.cmd == "exit":
                    self.send_data()
                    break
                if self.cmd == "shell":
                    self.cmd = "}shell"
                    self.send_data()
                    self.handle_io_rev_shell()
                else:
                    self.send_data()
                    self.recv_data()

    def prompt(self):
        prompt = ANSI("{fg.li_blue}TAL(•)N {fg.grey}[--|>{rs.all} ".format(
            **globals()))
        self.cmd = self.ps.prompt(prompt)

    def connect(self):
        self.socket.bind(self.addr)
        self.socket.listen(5)
        self.conn, self.r_addr = self.socket.accept()
        # self.conn.shutdown(socket.SHUT_WR)
        self.conn.setblocking(False)
        print(basic['B_CONN_ACCEPTED'].format(**globals()))

    def recv_data(self, EOF=None):
        self.bytes = b''
        while True:
            try:
                self.bytes = self.conn.recv(self.buf_size)
                if EOF and EOF.encode() in self.bytes:
                    self.bytes = self.bytes.replace(EOF.encode(), b'')
                    print(self.bytes.decode())
                    self.status = False
                    break
                print(self.bytes.decode(), end="")
                # sys.stdout.buffer.write(self.bytes)
                # print(bytes.decode("utf-8"), end="")
                sys.stdout.flush()
                if len(self.bytes) < self.buf_size:
                    break
            except(BlockingIOError):
                continue

    def send_data(self):
        try:
            data = self.cmd.encode()
            self.cmd = None
            self.conn.sendall(data)
        except socket.error as err:
            print(errors['E_CUSTOM'].format(**globals()), err)


if __name__ == "__main__":
    # talon_autocomplete = WordCompleter("new", "exit", "whoami")
    prompt = ANSI("{fg.li_cyan}TAL(•)N{rs.all} |> ".format(**globals()))
    charge_templates()
    parse_arguments()
    

    if not quiet:
        print_logo()
    addr_info = socket.getaddrinfo(host, port, type=socket.AF_INET)[0]
    ps = PromptSession()
    while True:
        cmd = ps.prompt(prompt)
        sessions = []
        if cmd == "exit":
            for elem in sessions:
                elem.kill()
            print("{fg.blue}[|>{fg.white}{ef.bold} ByE!!".format(**globals()))
            exit(0)
        elif cmd == "new":
            session = Session(host, port, buffer_size)
            print(basic['B_START_SES'].format(**globals()))
            sessions.append(session)
            session.start()
            print("nice")
        else:
            print(errors['E_UNKOWN_CMD'].format(**globals()))
