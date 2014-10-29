#!/usr/bin/python3
import asyncio
import concurrent.futures

import routers


class GopherServer(object):

    def __init__(self, host, port, router, loop=None):
        self.router = router
        self._loop = loop or asyncio.get_event_loop()
        self._server = asyncio.start_server(self.handle_gopher,
                                            host=host,
                                            port=port)

    def start(self, and_loop=True):
        self._server = self._loop.run_until_complete(self._server)
        if and_loop:
            self._loop.run_forever()

    def stop(self, and_loop=True):
        self._server.close()
        if and_loop:
            self._loop.close()

    @asyncio.coroutine
    def handle_gopher(self, reader, writer):
        data = yield from reader.readline()
        data = data.decode('utf-8').rstrip('\r\n')
        writer.writelines(self.router[data].display())

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
