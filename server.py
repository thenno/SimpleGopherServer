#!/usr/bin/python3
import abc
import multiprocessing
import os
import select
import socket
import threading

import connections
import routers


class Messanger(object):

    def __init__(self, message_bus, server_id):
        self.in_messages = multiprocessing.Queue()
        self.message_bus = message_bus
        self.server_id = server_id


class MessageRouter(Messanger, multiprocessing.Process):

    def __init__(self, message_bus, server_id):
        multiprocessing.Process.__init__(self)
        Messanger.__init__(self, message_bus, server_id)
        self.router = {}
        self.is_running = False

        self.register(self)

    def register(self, server):
        self.router[server.server_id] = server.in_messages

    def run(self):
        self.is_running = True
        while self.is_running:
            server_id, message = self.message_bus.get()
            if server_id == self.server_id:
                self.stop()
            self.router[server_id].put(message)

    def stop(self):
        self.is_running = False


class Server(multiprocessing.Process):

    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        multiprocessing.Process.__init__(self)
        self.config = config
        self.socket = self._init_socket()
        self.is_running = False

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def _init_socket(self):
        pass

    def stop(self):
        map(lambda x: x.join(), threading.enumerate())
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.is_running = False


class GopherServer(Server, Messanger):

    def __init__(self, message_bus, server_id, config):
        Server.__init__(self, config)
        Messanger.__init__(self, message_bus, server_id)
        self.router = self._get_router()

    def run(self):
        self.is_running = True
        while self.is_running:
            events = [self.socket, self.in_messages._reader]
            in_events, _, _ = select.select(events, [], [])
            for in_event in in_events:
                if in_event == self.socket:
                    open_con = connections.GopherConnection(in_event,
                                                            self.router)
                    open_con.start()
                elif self.in_messages:
                    if in_event.recv() == 'stop':
                        self.stop()

    def _init_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.config['server_name'],
                   self.config['server_port']))
        sock.listen(self.config['max_gopher_socket_listeners'])
        return sock

    def _get_router(self):
        index = routers.get_index(self.config['resources_directory'],
                                  self.config['server_name'],
                                  self.config['server_port'])

        return routers.get_router(index)


class ControlServer(Server, Messanger):

    def __init__(self, message_bus, server_id, config):
        Server.__init__(self, config)
        Messanger.__init__(self, message_bus, server_id)

    def run(self):
        self.is_running = True
        while self.is_running:
            in_events, _, _ = select.select([self.socket], [], [])
            for in_event in in_events:
                connections.ControlConnection(in_event,
                                              self.message_bus).start()

    def _init_socket(self):
        sock = socket.socket(socket.AF_UNIX)
        sock.bind(self.config['control_socket_file'])
        sock.listen(self.config['max_control_socket_listeners'])

        return sock

    def stop(self):
        super().stop()
        os.remove(self.config['control_socket_file'])


def main():
    config = {
        'max_gopher_socket_listeners': 10,
        'server_name': 'localhost',
        'server_port': 7070,
        'control_socket_file': 'socket_control',
        'resources_directory': 'content',
        'max_control_socket_listeners': 1,
    }
    message_bus = multiprocessing.Queue()
    message_router = MessageRouter(message_bus, 'router')
    controller = ControlServer(message_bus, 'controller', config)
    controller.start()
    message_router.register(controller)
    gopher_server = GopherServer(message_bus, 'gopher_server', config)
    gopher_server.start()
    message_router.register(gopher_server)
    message_router.start()
    print('Понеслась')

if __name__ == '__main__':
    main()
