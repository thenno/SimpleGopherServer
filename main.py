#!/usr/bin/python3
import argparse
import asyncio
import json
import signal

import log
import routers
import server


class Manager(object):

    def load_config(self):
        alogger = log.TSKVLoggerAdapter(self.logger,
                                        {'action': 'load_config',
                                         'path': self._config_path})
        try:
            with open(self._config_path) as config_file:
                return json.load(config_file)
        except IOError:
            alogger.error({'error': 'invalid config file path'})
            exit(1)
        except ValueError:
            alogger.error({'error': 'invalid config file format'})
            exit(1)

        alogger.info({'result': 'success'})

    def init_signals(self):
        self._loop.add_signal_handler(signal.SIGTERM,
                                      self.stop)
        self._loop.add_signal_handler(signal.SIGINT,
                                      self.stop)
        self._loop.add_signal_handler(signal.SIGUSR1,
                                      self.restart)

    def start(self):
        self._config = self.load_config()

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self.init_signals()

        _index = routers.get_index(self._config['content_dir'],
                                   self._config['server'],
                                   self._config['port'])
        _router = routers.get_router(_index)
        self._server = server.GopherServer(self._config['server'],
                                           self._config['port'],
                                           _router,
                                           self._loop)
        self._server.start()
        self._loop.run_forever()

    def stop(self):
        self._server.stop()
        self._loop.call_soon(self._loop.stop())

    def restart(self):
        self.stop()
        self.start()

    def sigusr2_handler(self):
        self.load_config()

    def __init__(self, config_path='config.json'):
        self.logger = log.get_logger('manager')
        self._config_path = config_path

        self._loop = None
        self._config = None
        self._server = None


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--config', '-c', type=str,
                            default='config.json', help="Path to config file")

    args = arg_parser.parse_args()
    manager = Manager(args.config)
    manager.start()

