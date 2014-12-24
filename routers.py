#!/usr/bin/python3
import functools
import os

import log
import resources
import utils


resource_types = {
    'directory': resources.ResourceDirectory,
    'file': resources.ResourceFile,
}


def get_index(source_path, config, server, port):
    logger = log.get_logger('indexer')
    alogger = log.TSKVLoggerAdapter(logger, {'server': server,
                                             'port': port})

    alogger.info({'action': 'start indexing',
                  'path': source_path})

    global_menu = resources.ResourceDirectory(
        'start',
        '',
        server,
        port,
        None,
    )

    if not os.path.isdir(source_path):
        alogger.warning({'action': 'start indexing',
                         'error': 'Path is not directory',
                         'path': source_path})

    for raw_path, directories, files in os.walk(source_path):
        path = raw_path.replace(source_path, '', 1)

        dir_config_path = utils.mkpath(source_path, path, config)
        if os.path.exists(dir_config_path):
            alogger.debug({'action': 'parsing config for dir',
                           'path': dir_config_path})
            dir_config = utils.load_config(dir_config_path, alogger)

        # extract submenu by path
        menu = functools.reduce(lambda m, p: m[p],
                                utils.get_path_prefixes(path.split('/')),
                                global_menu)

        for resource_type, raw_resources in [('directory', directories),
                                             ('file', files)]:
            for resource in (r for r in raw_resources
                             if not r.startswith('.')):
                alogger.debug({'action': 'indexing',
                               'path': utils.mkpath(path, resource),
                               'type': resource_type})

                factory = resource_types[resource_type]
                resouce_path = utils.mkpath(source_path, path, resource)
                try:
                    menu.add(factory(
                        resource,
                        utils.mkpath(path, resource),
                        server,
                        port,
                        resouce_path,
                    ))
                except UnicodeDecodeError:
                    alogger.warning({'action': 'indexing',
                                     'path': resouce_path,
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
