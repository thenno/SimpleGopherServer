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


class TSKVLogger(object):

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def _log(self, level, msg):
        self.logger._log(level, TSKVMessage(**msg), (), {})

    def debug(self, msg):
        self._log(logging.DEBUG, msg)

    def info(self, msg):
        self._log(logging.INFO, msg)

    def warning(self, msg):
        self._log(logging.WARNING, msg)

    def error(self, msg):
        self._log(logging.ERROR, msg)

    def critical(self, msg):
        self._log(logging.CRITICAL, msg)


class TSKVLoggerAdapter(object):

    def __init__(self, logger, default=None):
        if default is None:
            default = {}
        self.default = default
        self.logger = logger

    def _log(self, level, msg):
        message = dict(msg, **self.default)
        self.logger._log(level, message)

    def debug(self, msg):
        self._log(logging.DEBUG, msg)

    def info(self, msg):
        self._log(logging.INFO, msg)

    def warning(self, msg):
        self._log(logging.WARNING, msg)

    def error(self, msg):
        self._log(logging.ERROR, msg)

    def critical(self, msg):
        self._log(logging.CRITICAL, msg)


def set_logging():
    logging.getLogger('asyncio').disabled = True
    log_format = 'level=%(levelname)s\tlog_name=%(name)s\t%(message)s\t' + \
                 'pid=%(process)d\tdate=%(asctime)s\t'
    logging.basicConfig(format=log_format,
                        level=logging.DEBUG)


set_logging()

def get_logger(name):
    return TSKVLogger(name)
