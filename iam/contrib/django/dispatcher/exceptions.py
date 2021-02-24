# -*- coding: utf-8 -*-


class DispatchBaseException(Exception):
    pass


class InvalidPageException(DispatchBaseException):
    pass


class KeywordTooShortException(DispatchBaseException):
    pass
