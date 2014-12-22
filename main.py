#!/usr/bin/python3
import argparse
import asyncio
import json
import signal

import log
import routers
import server


class Manager(object):

    def _load_config(self, path):
        alogger = log.TSKVLoggerAdapter(self.logger,
                                        {'action': 'load config',
                                         'path': self._config_path})
        try:
            with open(path) as config_file:
                return json.load(config_file)
        except IOError:
            alogger.error({'error': 'invalid config file path'})
            exit(1)
        except ValueError:
            alogger.error({'error': 'invalid config file format'})
            exit(1)

        alogger.info({'result': 'success'})

    def _init_log_system(self):
        log.init_log_system(self._config['logging'])

    def _reinit_log_system(self):
        self.logger.info({'action': 'reload config, restart log system'})
        self._config = self._load_config(self._config_path)
        log.init_log_system(self._config['logging'])

    def _init_signals(self):
        self._loop.add_signal_handler(signal.SIGTERM,
                                      self.stop)
        self._loop.add_signal_handler(signal.SIGINT,
                                      self.stop)
        self._loop.add_signal_handler(signal.SIGUSR1,
                                      self.restart)
        self._loop.add_signal_handler(signal.SIGUSR2,
                                      self._reinit_log_system)

    def start(self):
        self._config = self._load_config(self._config_path)
        self._init_log_system()

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._init_signals()

        server_config = self._config['server']
        _index = routers.get_index(server_config['content_dir'],
                                   server_config['server'],
                                   server_config['port'])
        _router = routers.get_router(_index)
        self._server = server.GopherServer(server_config['server'],
                                           server_config['port'],
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

    def __init__(self, config_path='config.json'):
        self.logger = log.get_logger('manager')
        self._config_path = config_path

        self._loop = None
        self._server = None
        self._config = None


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--config', '-c', type=str,
                            default='config.json',
                            help="Path to config file")

    args = arg_parser.parse_args()

    manager = Manager(args.config)
    manager.start()
