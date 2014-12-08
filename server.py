#!/usr/bin/python3
import asyncio
import concurrent.futures

import log
import routers
import utils


class GopherServer(object):

    def __init__(self, host, port, router, loop=None):
        self.logger = log.get_logger('gopher_server')

        self.router = router
        self._loop = loop or asyncio.get_event_loop()
        self._server = asyncio.start_server(self.handle_gopher,
                                            host=host,
                                            port=port)
        self.logger.info({'action': 'gopher_server_init'})

    def start(self):
        self.logger.info({'action': 'gopher_server_start'})
        self._server = self._loop.run_until_complete(self._server)
        self._loop.run_forever()

    def stop(self):
        self._server.close()
        self._loop.close()
        self.logger.info({'action': 'gopher_server_stop'})

    @asyncio.coroutine
    def handle_gopher(self, reader, writer):
        peer = writer.get_extra_info('peername')[0]

        try:
            request = yield from asyncio.wait_for(reader.readline(),
                                                  timeout=5)
            request = request.decode('utf-8').rstrip(utils.EOF.decode('utf-8'))
            if request in self.router:
                answer = list(self.router[request].display())
            else:
                answer = [b'invalid uri' + utils.EOF]

            writer.writelines(answer)
            self.logger.info({'action': 'gopher_connection',
                              'peer': peer,
                              'result': 'success',
                              'request': request,
                              'answer': answer})
        except concurrent.futures.TimeoutError:
            self.logger.info({'action': 'gopher_connection',
                              'peer': peer,
                              'result': 'timeout'})
        except BaseException as e:
            self.logger.error({'action': 'gopher_connection',
                               'peer': peer,
                               'result': 'unknown error',
                               'error': e})
        finally:
            if writer.can_write_eof():
                writer.write_eof()
            writer.close()


def main():

    index = routers.get_index('content', 'localhost', 7070)
    router = routers.get_router(index)
    server = GopherServer('localhost', 7070, router)

    try:
        server.start()
    except KeyboardInterrupt:
        pass  # Press Ctrl+C to stop
    finally:
        server.stop()

if __name__ == '__main__':
    main()
