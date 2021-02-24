# -*- coding: utf-8 -*-


from django.http.response import JsonResponse

from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE


class IAMAuthFailedResponse(JsonResponse):
    def __init__(self, exc, *args, **kwargs):
        kwargs["data"] = {
            "result": False,
            "code": HTTP_AUTH_FORBIDDEN_CODE,
            "message": "you have no permission to operate",
            "data": None,
            "permission": exc.perms_apply_data(),
        }
        kwargs['status'] = kwargs.get("status", 499)
        super(IAMAuthFailedResponse, self).__init__(*args, **kwargs)
