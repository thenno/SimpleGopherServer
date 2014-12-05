#!/usr/bin/python3
import functools
import os

import log
import resources
import utils


def get_index(source_path, server, port):
    logger = log.get_logger('indexer')

    logger.info({'action': 'indexing',
                 'path': source_path,
                 'server': server,
                 'port': port})

    global_menu = resources.ResourceDirectory(
        'start',
        '',
        server,
        port,
    )

    for raw_path, directories, files in os.walk(source_path):
        path = '/'.join(raw_path.split('/')[1:])
        path = '/' + path if path else ''

        # extract submenu by path
        menu = functools.reduce(lambda m, p: m[p],
                                utils.get_path_prefixes(path.split('/')),
                                global_menu)

        for directory in directories:
            menu.add(resources.ResourceDirectory(
                directory,
                utils.mkpath(path, directory),
                server,
                port,
            ))


        # exclude dotfiles
        for file_ in (f for f in files if not f.startswith('.')):
            menu.add(resources.ResourceFile(
                file_,
                utils.mkpath(path, file_),
                server,
                port,
                utils.mkpath(source_path, path, file_)
            ))

    return global_menu


def get_router(index, router=None):
    if router is None:
        logger = log.get_logger('router')
        router = {'': index}
        logger.info({'action': 'get_router',
                     'from': type(index),
                     'from_type': 'index'})

    for route, item in index.items():
        router[route] = item
        if isinstance(item, resources.ResourceDirectory):
            router.update(get_router(item, router))

    return router
