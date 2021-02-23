# -*- coding: utf-8 -*-

import unittest

from iam import Converter

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class BaseConverterTest(unittest.TestCase):
    """
    for abstractmethod, make sure no absent
    """
    @patch.object(Converter, '__abstractmethods__', set())
    def test(self):
        self.instance = Converter()

        self.instance._eq(1, 1)
        self.instance._not_eq(1, 1)
        self.instance._in(1, 1)
        self.instance._not_in(1, 1)
        self.instance._contains(1, 1)
        self.instance._not_contains(1, 1)
        self.instance._starts_with(1, 1)
        self.instance._not_starts_with(1, 1)
        self.instance._ends_with(1, 1)
        self.instance._not_ends_with(1, 1)

        self.instance._lt(1, 1)
        self.instance._lte(1, 1)
        self.instance._gt(1, 1)
        self.instance._gte(1, 1)

        self.instance._any(1, 1)

        self.instance._and(1)
        self.instance._or(1)

        self.instance.convert(None)
