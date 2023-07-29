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
                        metavar="buffer_size", type=int, default=2048)
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
        # except ValueError:
        # print(errors['E_INVALID_IP'].format(**globals()))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def kill(self):
        self.socket.close()

    def start(self):
        try:
            
            self.connect()
            self.handle_io_rev_shell()
            # self.handle_io()
                
            self.socket.close()
            print(basic['B_END_SES'].format(**globals()))
        except socket.error as err:
            print(errors['E_CUSTOM'].format(**globals()), err)

    def handle_io_rev_shell(self):
        set_nonblocking(sys.stdin)
        set_nonblocking(sys.stdout)
       
        while True and self.status: 
            sin = [self.conn, sys.stdin]  
            rs, _, _, = select.select(sin, [], [])
            if self.conn in rs:
                self.recv_data()
            if sys.stdin in rs:
                self.cmd = sys.stdin.read(1080)
                self.send_data()
    
    def handle_io(self):
        while True and self.status:
            self.prompt()
            if self.cmd == "exit":
                break 
            self.send_data()
            try:
                self.recv_data()
            except (BlockingIOError):
                rs, _, _= select.select([self.conn], [], [])
                self.recv_data()
            # rs, _, _ =  select.select([self.conn], [], [])
            rs, ws, _ = select.select([self.conn], [self.conn], [])
            if rs:
                print("checkpoint")
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
        self.status = True
        print(basic['B_CONN_ACCEPTED'].format(**globals()))

    def recv_data(self):
        self.buffer = self.conn.recv(self.buf_size)
        print(self.buffer)
        # print((b''.join(self.buffer)).decode(), end='')
        # PRUEBAS QUE SE REALIZARON CON LA REVERSESHELL
        # sys.stdout.write(b''.join(self.buffer).decode())
        # print(b''.join(self.buffer).decode(), end="")
        # sys.stdout.flush()
        # print(b''.join(self.buffer).decode(), end="")
        # print(json.loads((b''.join(self.buffer)).decode('utf-8')))
         

    def send_data(self):
        # try:
        data = (self.cmd).encode()
        self.conn.sendall(data)
        # except socket.error as err:
        # print(errors['E_CUSTOM'].format(**globals()), err)


if __name__ == "__main__":
    # talon_autocomplete = WordCompleter("new", "exit", "whoami")
    prompt = ANSI("{fg.li_cyan}TAL(•)N{rs.all} |> ".format(**globals()))
    charge_templates()
    parse_arguments()
    
    # set_nonblocking(sys.stdout)
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
            session.start()
            print("nice")
        else:
            print(errors['E_UNKOWN_CMD'].format(**globals()))
