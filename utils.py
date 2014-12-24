#!/usr/bin/python3
import json
import log

EOF = b'\r\n'
ERROR_HOST = 'error.host'
ERROR_PORT = 1

def get_path_prefixes(elems):
    sum_ = ''
    for elem in elems:
        if elem:
            sum_ += '/' + elem
            yield sum_


def mkpath(*elems):
    return '/'.join(elems)


def load_config(path, logger):
    alogger = log.TSKVLoggerAdapter(logger,
                                    {'action': 'load config',
                                     'path': path})
    try:
        with open(path) as config_file:
            config = json.load(config_file)
            alogger.info({'result': 'success'})
            return config
    except IOError:
        alogger.error({'error': 'invalid config file path'})
    except ValueError:
        alogger.error({'error': 'invalid config file format'})
