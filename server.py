#!/usr/bin/python3
import asyncio
import concurrent.futures

import log
import utils


class GopherServer(object):

    def __init__(self, host, port, router, loop):

        self.logger = log.get_logger('gopher_server')

        self.router = router
        self._loop = loop
        self._server = asyncio.start_server(self.handle_gopher,
                                            host=host,
                                            port=port)
        self.logger.info({'action': 'gopher_server_init'})

    def start(self):
        self.logger.info({'action': 'gopher_server_start'})
        self._server = self._loop.run_until_complete(self._server)

    def stop(self):
        self._server.close()
        self.logger.info({'action': 'gopher_server_stop'})

    @asyncio.coroutine
    def handle_gopher(self, reader, writer):
        peer = writer.get_extra_info('peername')[0]
        alogger = log.TSKVLoggerAdapter(self.logger,
                                        {'action': 'gopher_connection',
                                         'peer': peer})

        try:
            request = yield from asyncio.wait_for(reader.readline(),
                                                  timeout=5)
            request = request.decode('utf-8').rstrip(utils.EOF.decode('utf-8'))
            if request in self.router:
                answer = list(self.router[request].display())
            else:
                answer = [b'invalid uri' + utils.EOF]

            writer.writelines(answer)
            alogger.info({'request': request,
                          'answer': answer})
        except concurrent.futures.TimeoutError:
            alogger.info({'error': 'timeout'})
        except BaseException as e:
            alogger.info({'error': e})
        finally:
            if writer.can_write_eof():
                writer.write_eof()
            writer.close()
