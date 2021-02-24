# -*- coding: utf-8 -*-


class FancyDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        # 内建属性不放入 key 中
        if key.startswith("__") and key.endswith("__"):
            super(FancyDict, self).__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)
