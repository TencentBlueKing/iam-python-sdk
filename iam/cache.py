# -*- coding: utf-8 -*-



def hash_key(*args):
    args = args[1:]
    return tuple(hash(k) for k in args)
