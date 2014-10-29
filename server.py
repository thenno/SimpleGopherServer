#!/usr/bin/python3
import multiprocessing
import socket
import threading

import routers


class GopherConnection(multiprocessing.Process):
    def __init__(self, conn, router):
        multiprocessing.Process.__init__(self)
        self.conn = conn
        self.router = router

    def run(self):
        data = self.conn.recv(1024).decode("utf-8").rstrip('\r\n')
        self.router[data].send_data(self.conn)
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()


class GopherServer(threading.Thread):

    def __init__(self, host, port, router):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(10)
        self.router = router

        self.is_running = False
        self.opened_connections = []

    def run(self):
        self.is_running = True
        while self.is_running:
            conn, adress = self.socket.accept()
            open_conn = GopherConnection(conn, self.router)
            open_conn.start()

    def stop(self):
        self.is_running = False
        for children in multiprocessing.active_children():
            children.join(5)
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


def main():
    index = routers.get_index('content', 'localhost', 7070)
    router = routers.get_router(index)
    gopher_server = GopherServer('localhost', 7070, router)
    gopher_server.start()


if __name__ == '__main__':
    main()
