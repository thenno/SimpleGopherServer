#!/usr/bin/python3
import functools
import os

import log
import resources
import utils


RESOURCE_TYPE_FACTORIES = {
    'directory': resources.ResourceDirectory,
    'file': resources.ResourceFile,
}


def indexing_path(source_path):
    for raw_path, directories, files in os.walk(source_path):
        for directory in directories:
            yield (raw_path, directory, 'directory')
        for file_ in (f for f in files if not f.startswith('.')):
            yield (raw_path, file_, 'file')


def get_index(source_path, server, port):

    full_source_path = os.path.realpath(source_path)

    global_menu = resources.ResourceDirectory(
        'start',
        '',
        server,
        port,
        None,
    )

    for path, name, type_ in indexing_path(full_source_path):

        menu_path = path.replace(full_source_path, '', 1)
        selector = menu_path + '/' + name
        fs_path = os.path.join(full_source_path, path, name)

        logger = log.TSKVLoggerAdapter(
            log.get_logger('indexing'),
            {'action': 'indexing',
             'selector': selector,
             'server': server,
             'port': port,
             'fs_path': fs_path,
             'type': type_},
        )

        # extract submenu by path
        menu = functools.reduce(lambda m, p: m[p],
                                utils.get_path_prefixes(menu_path),
                                global_menu)

        factory = RESOURCE_TYPE_FACTORIES[type_]
        logger.debug({
            'status': 'start_indexing',
        })
        try:
            menu.add(factory(
                name,
                selector,
                server,
                port,
                fs_path,
            ))
        except UnicodeDecodeError:
            logger.warning({
                'status': 'unicode error',
            })

    return global_menu


def get_router(index, router=None):
    logger = log.get_logger('router')
    logger.info({'action': 'get_router',
                 'from': index.items(),
                 'from_type': 'index'})

    if router is None:
        router = {'': index}

    for route, item in index.items():
        router[route] = item
        if isinstance(item, resources.ResourceDirectory):
            router.update(get_router(item, router))

    return router
