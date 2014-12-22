#!/usr/bin/python3
import functools
import os

import log
import resources
import utils


def get_index(source_path, server, port):
    logger = log.get_logger('indexer')
    alogger = log.TSKVLoggerAdapter(logger, {'action': 'indexing',
                                             'server': server,
                                             'port': port})

    alogger.info({'path': source_path})

    global_menu = resources.ResourceDirectory(
        'start',
        '',
        server,
        port,
    )

    if not os.path.isdir(source_path):
        alogger.warning({'error': '{0} is not directory'.format(source_path)})

    for raw_path, directories, files in os.walk(source_path):
        path = raw_path.replace(source_path, '', 1)
        path = path if path else ''

        # extract submenu by path
        menu = functools.reduce(lambda m, p: m[p],
                                utils.get_path_prefixes(path.split('/')),
                                global_menu)

        for directory in directories:
            alogger.debug({'path': utils.mkpath(path, directory),
                           'type': 'dir'})
            menu.add(resources.ResourceDirectory(
                directory,
                utils.mkpath(path, directory),
                server,
                port,
            ))


        # exclude dotfiles
        for file_ in (f for f in files if not f.startswith('.')):
            alogger.debug({'path': utils.mkpath(path, file_),
                           'type': 'file'})
            try:
                menu.add(resources.ResourceFile(
                    file_,
                    utils.mkpath(path, file_),
                    server,
                    port,
                    utils.mkpath(source_path, path, file_)
                ))
            except UnicodeDecodeError:
                alogger.warning({'path': utils.mkpath(path, file_),
                                 'error': 'File is not utf-8'})

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
