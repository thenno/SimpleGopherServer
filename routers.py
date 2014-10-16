#!/usr/bin/python3

import resources


def get_router_from_index(index, router=None):
    if router is None:
        router = {'': index}

    for route, item in index.items():
        router[route] = item
        if isinstance(item, resources.ResourceDirectory):
            router.update(get_router_from_index(item, router))

    return router
