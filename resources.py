#!/usr/bin/python3
import abc
from collections import OrderedDict

import utils


RESOURCE_TYPES = {
    'plain_text_file': 0,
    'directory': 1,
    'info': 'i',
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
        ])

    @abc.abstractmethod
    def display(self):
        pass


class ResourceDirectory(Resource):

    def __init__(self, display_string, selector, host, port, extra):
        super().__init__(
            RESOURCE_TYPES['directory'], display_string, selector, host, port,
        )
        self._resources = OrderedDict()

    def __iter__(self):
        return self._resources.__iter__()

    def __getitem__(self, item):
        return self._resources[item]

    def add(self, item):
        self._resources[item.selector] = item

    def items(self):
        return self._resources.items()

    def display(self):
        for resource in self._resources.values():
            yield resource.as_menu_item().encode("utf-8") + utils.EOF
        yield b'.' + utils.EOF


class ResourceFile(Resource):

    def __init__(self, display_string, selector, host, port, extra):
        path = extra

        super().__init__(
            RESOURCE_TYPES['plain_text_file'],
            display_string,
            selector,
            host,
            port,
        )
        with open(path) as f:
            self.content = [line for line in f]

    def display(self):
        for line in self.content:
            yield line.encode("utf-8")
        yield utils.EOF + b'.' + utils.EOF


class ResourceInfo(Resource):

    def __init__(self, display_string, selector, host, port, extra):
        self.message = display_string
        super().__init__(
            RESOURCE_TYPES['info'], display_string, selector, host, port
        )

    def as_menu_item(self):
        return self.resource_type + self.message

    def display(self):
        yield self.message.encode("utf-8") + utils.EOF
