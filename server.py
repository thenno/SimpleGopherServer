#!/usr/bin/python3
import socket
import indexers
import routers
import threading


class GopherConnection(threading.Thread):
    def __init__(self, conn, addr, router):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.router = router

    def run(self):
        data = self.conn.recv(1024)
        self.router[data.decode("utf-8").rstrip('\r\n')].send_data(conn)
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()


SERVER_NAME = "localhost"
SERVER_PORT = 7070

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_NAME, SERVER_PORT))
server_socket.listen(10)

index = indexers.get_resources_from_fs('content', SERVER_NAME, SERVER_PORT)
router = routers.get_router_from_index(index)

try:
    while True:
        conn, addr = server_socket.accept()
        connection = GopherConnection(conn, addr, router)
        connection.start()
finally:
    server_socket.close()
