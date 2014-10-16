#!/usr/bin/python3

import abc


RESOURCE_TYPES = {
    'file': 0,
    'directory': 1,
}


class Resource(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, resource_type, display_string, selector, host, port):
        self.resource_type = str(resource_type)
        self.display_string = str(display_string)
        self.selector = str(selector)
        self.host = str(host)
        self.port = str(port)

    def __hash__(self):
        return self.selector.__hash__()

    def __str__(self):
        return self.selector

    def as_menu_item(self):
        return '\t'.join([
            self.resource_type + self.display_string,
            self.selector,
            self.host,
            self.port,
        ]) + '\r\n'

    @abc.abstractmethod
    def send_data(self, socket):
        pass


class ResourceDirectory(Resource):

    def __init__(self, display_string, selector, host, port):
        super().__init__(
            RESOURCE_TYPES['directory'], display_string, selector, host, port,
        )
        self._resources = {}

    def __iter__(self):
        return self._resources.__iter__()

    def __getitem__(self, item):
        return self._resources[item]

    def add(self, item):
        self._resources[item.selector] = item

    def items(self):
        return self._resources.items()

    def send_data(self, socket):
        for resource in self._resources.values():
            socket.send(resource.as_menu_item().encode("utf-8"))
        socket.send(b".\r\n")


class ResourceFile(Resource):

    def __init__(self, display_string, selector, host, port, path):
        super().__init__(
            RESOURCE_TYPES['file'], display_string, selector, host, port,
        )
        with open(path) as f:
            self.content = [line for line in f]

    def send_data(self, socket):
        for line in self.content:
            socket.send(line.encode("utf-8"))
        socket.send(b'\r\n.\r\n')
