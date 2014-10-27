#!/usr/bin/python3


def get_path_prefixes(elems):
    sum_ = ''
    for elem in elems:
        if elem:
            sum_ += '/' + elem
            yield sum_


def mkpath(*elems):
    return '/'.join(elems)
