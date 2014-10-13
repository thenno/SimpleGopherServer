#!/usr/bin/python
import socket
import indexers
import routers


SERVER_NAME = "localhost"
SERVER_PORT = 7070

server_socket = socket.socket()
server_socket.bind((SERVER_NAME, SERVER_PORT))
server_socket.listen(10)

index = indexers.get_resources_from_fs('content', SERVER_NAME, SERVER_PORT)
router = routers.get_router_from_index(index)

while True:
    conn, addr = server_socket.accept()
    data = conn.recv(1024)
    router[data.rstrip('\r\n')].send_data(conn)
    conn.close()
