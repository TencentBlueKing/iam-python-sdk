# -*- coding: utf-8 -*-


from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from iam.contrib.django.response import IAMAuthFailedResponse
from iam.exceptions import AuthFailedBaseException


class AuthFailedExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, AuthFailedBaseException):
            api_prefix = getattr(settings, "BK_IAM_API_PREFIX", "")
            status_code = 200 if api_prefix and request.path.startswith(api_prefix) else 499
            return IAMAuthFailedResponse(exception, status=status_code)
