#!/ysr/bin/python3
import socket
import threading


class GopherConnection(threading.Thread):
    def __init__(self, sock, router):
        threading.Thread.__init__(self)
        conn, addr = sock.accept()
        self.conn = conn
        self.addr = addr
        self.router = router

    def run(self):
        data = self.conn.recv(1024).decode("utf-8")
        self.router[data.rstrip('\r\n')].send_data(self.conn)
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()


class ControlConnection(threading.Thread):
    def __init__(self, sock, messages):
        threading.Thread.__init__(self)
        conn, addr = sock.accept()
        self.conn = conn
        self.addr = addr
        self.messages = messages

    def run(self):
        data = eval(self.conn.recv(1024).decode("utf-8").rstrip('\n'))
        self.messages.put(data)
        self.conn.close()
