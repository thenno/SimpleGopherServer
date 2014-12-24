#!/usr/bin/python3
import asyncio
import argparse
import signal

import log
import routers
import server
import utils


class Manager(object):

    def _init_log_system(self):
        log.init_log_system(self._config['logging'])

    def _reinit_log_system(self):
        self._logger.info({'action': 'reload config, restart log system'})
        self._config = utils.load_config(self._config_path, self._logger)
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
        self._config = utils.load_config(self._config_path, self._logger)
        self._init_log_system()

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._init_signals()

        server_config = self._config['server']
        _index = routers.get_index(server_config['content_dir'],
                                   server_config['config_dir_file'],
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
        self._logger = log.get_logger('manager')
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
