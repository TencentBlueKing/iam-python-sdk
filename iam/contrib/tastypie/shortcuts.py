# -*- coding: utf-8 -*-



from tastypie.exceptions import ImmediateHttpResponse

from iam import Request
from iam.exceptions import AuthFailedException, MultiAuthFailedException
from iam.contrib.django.response import IAMAuthFailedResponse


def allow_or_raise_immediate_response(iam, system, subject, action, resources, environment=None):
    request = Request(system, subject, action, resources, environment)

    allowed = iam.is_allowed(request)

    if not allowed:
        raise ImmediateHttpResponse(IAMAuthFailedResponse(AuthFailedException(system, subject, action, resources)))

    return


def allow_or_raise_immediate_response_for_resources_list(
    iam, system, subject, action, resources_list, environment=None
):
    if not resources_list:
        return

    resources_map = {}
    for resources in resources_list:
        resources_map[resources[0].id] = resources

    request = Request(system, subject, action, [], environment)
    result = iam.batch_is_allowed(request, resources_list)

    if not result:
        raise MultiAuthFailedException(system, subject, action, resources_list)

    not_allowed_list = []
    for tid, allow in result.items():
        if not allow:
            not_allowed_list.append(resources_map[tid])

    if not_allowed_list:
        raise MultiAuthFailedException(system, subject, action, not_allowed_list)

    return
