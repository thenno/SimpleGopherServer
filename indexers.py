#!/usr/bin/python3

import os
import resources
import functools


def get_path_prefixes(elems):
    sum_ = ''
    for el in elems:
        if el:
            sum_ += '/' + el
            yield sum_


def mkpath(*elems):
    return '/'.join(elems)


def get_resources_from_fs(source_path, server, port):
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
                                get_path_prefixes(path.split('/')),
                                global_menu)

        for directory in directories:
            menu.add(resources.ResourceDirectory(
                directory,
                mkpath(path, directory),
                server,
                port,
            ))

        for file_ in files:
            menu.add(resources.ResourceFile(
                file_,
                mkpath(path, file_),
                server,
                port,
                mkpath(source_path, path, file_)
            ))

    return global_menu
