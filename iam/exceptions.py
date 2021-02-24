# -*- coding: utf-8 -*-


import abc

import six

from .utils import gen_perms_apply_data


class AuthBaseException(Exception):
    pass


class AuthAPIError(AuthBaseException):
    pass


class AuthInvalidRequest(AuthBaseException):
    pass


class AuthInvalidParam(AuthBaseException):
    pass


class AuthInvalidOperation(AuthBaseException):
    pass


@six.add_metaclass(abc.ABCMeta)
class AuthFailedBaseException(AuthBaseException):
    @abc.abstractmethod
    def perms_apply_data(self):
        raise NotImplementedError()


class AuthFailedException(AuthFailedBaseException):
    def __init__(self, system, subject, action, resources):
        self.system = system
        self.subject = subject
        self.action = action
        self.resources = resources

    def perms_apply_data(self):
        return gen_perms_apply_data(
            self.system, self.subject, [{"action": self.action, "resources_list": [self.resources]}]
        )


class MultiAuthFailedException(AuthFailedBaseException):
    def __init__(self, system, subject, action, resources_list):
        self.system = system
        self.subject = subject
        self.action = action
        self.resources_list = resources_list

    def perms_apply_data(self):
        return gen_perms_apply_data(
            self.system, self.subject, [{"action": self.action, "resources_list": self.resources_list}]
        )


class RawAuthFailedException(AuthFailedBaseException):
    def __init__(self, permissions):
        self.permissions = permissions

    def perms_apply_data(self):
        return self.permissions
