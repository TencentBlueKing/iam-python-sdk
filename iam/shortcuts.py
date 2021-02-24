# -*- coding: utf-8 -*-


from . import Request
from .exceptions import AuthFailedException


def allow_or_raise_auth_failed(iam, system, subject, action, resources, environment=None):
    request = Request(system, subject, action, resources, environment)

    allowed = iam.is_allowed(request)

    if not allowed:
        raise AuthFailedException(system, subject, action, resources)

    return
