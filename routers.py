#!/usr/bin/python

import resources


def get_router_from_index(index, router={}):
    if not router:
        router[''] = index

    for route, item in index.iteritems():
        router[route] = item
        if isinstance(item, resources.ResourceDirectory):
            router.update(get_router_from_index(item, router))
    return router
