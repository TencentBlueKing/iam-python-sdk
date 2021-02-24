# -*- coding: utf-8 -*-


import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Converter(object):
    def __init__(self, key_mapping=None):
        self.key_mapping = key_mapping

    @abc.abstractmethod
    def _eq(self, left, right):
        pass

    @abc.abstractmethod
    def _not_eq(self, left, right):
        pass

    @abc.abstractmethod
    def _in(self, left, right):
        pass

    @abc.abstractmethod
    def _not_in(self, left, right):
        pass

    @abc.abstractmethod
    def _contains(self, left, right):
        pass

    @abc.abstractmethod
    def _not_contains(self, left, right):
        pass

    @abc.abstractmethod
    def _starts_with(self, left, right):
        pass

    @abc.abstractmethod
    def _not_starts_with(self, left, right):
        pass

    @abc.abstractmethod
    def _ends_with(self, left, right):
        pass

    @abc.abstractmethod
    def _not_ends_with(self, left, right):
        pass

    @abc.abstractmethod
    def _lt(self, left, right):
        pass

    @abc.abstractmethod
    def _lte(self, left, right):
        pass

    @abc.abstractmethod
    def _gt(self, left, right):
        pass

    @abc.abstractmethod
    def _gte(self, left, right):
        pass

    @abc.abstractmethod
    def _any(self, left, right):
        pass

    @abc.abstractmethod
    def _and(self, content):
        pass

    @abc.abstractmethod
    def _or(self, content):
        pass

    @abc.abstractmethod
    def convert(self, data):
        pass
