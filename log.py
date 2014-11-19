#!/usr/bin/python3

import logging


class TSKVMessage(object):
    _kv_delimiter = '='
    _delimiter = '\t'

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def _quote(self, value):
        return str(value).encode('unicode_escape').decode('utf-8')

    def _quote_key(self, key):
        return self._quote(key).replace('=', r'\=')

    def _build_pair(self, key, value):
        return "{0}={1}".format(self._quote_key(key), self._quote(value))

    def __str__(self):
        pairs = (self._build_pair(key, value)
                 for key, value in self.kwargs.items())
        return self._delimiter.join(sorted(pairs))


class TSKVLogger(logging.getLoggerClass()):

    def debug(self, msg, *args, **kwargs):
        super().debug(TSKVMessage(**msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        super().info(TSKVMessage(**msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        super().warning(TSKVMessage(**msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        super().error(TSKVMessage(**msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        super().critical(TSKVMessage(**msg), *args, **kwargs)


def set_logging():
    logging.getLogger('asyncio').disabled = True
    log_format = 'level=%(levelname)s\t%(message)s\t' + \
                 'source=%(filename)s:%(funcName)s:%(lineno)d' + \
                 '\tdate=%(asctime)s\t'
    logging.basicConfig(format=log_format,
                        level=logging.DEBUG)


set_logging()

def get_logger(name):
    logging.setLoggerClass(TSKVLogger)
    return logging.getLogger(name)
