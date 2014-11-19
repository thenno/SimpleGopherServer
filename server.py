#!/usr/bin/python3
import asyncio

import log
import routers


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
        self.logger.info({'action': 'gopher_server_stop'})
        self._server = self._loop.run_until_complete(self._server)
        self._loop.run_forever()

    def stop(self):
        self._server.close()
        self._loop.close()
        self.logger.info({'action': 'gopher_server_stop'})

    @asyncio.coroutine
    def handle_gopher(self, reader, writer):
        peer = writer.get_extra_info('peername')

        request = yield from reader.readline()
        request = request.decode('utf-8').rstrip('\r\n')
        answer = self.router[request].display()
        writer.writelines(answer)

        self.logger.info({'action': 'gopher_connection',
                          'peer': peer[0],
                          'request': request,
                          'answer': list(self.router[request].display())})

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
        pass # Press Ctrl+C to stop
    finally:
        server.stop()

if __name__ == '__main__':
    main()
