# -*- coding: utf-8 -*-

import pytest
# import unittest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock


from iam.exceptions import AuthBaseException, AuthAPIError, AuthInvalidRequest, AuthInvalidParam, AuthFailedException


def test_exceptions():

    with pytest.raises(AuthBaseException):
        raise AuthAPIError

    with pytest.raises(AuthBaseException):
        raise AuthInvalidRequest

    with pytest.raises(AuthBaseException):
        raise AuthInvalidParam


def test_auth_failed_exception():
    gen_perms_apply_data = MagicMock(return_value="gen_perms_apply_data_token")
    with patch("iam.exceptions.gen_perms_apply_data", gen_perms_apply_data):
        abe = AuthFailedException("system", "subject", "action", ["resources"])
        data = abe.perms_apply_data()

    assert data == "gen_perms_apply_data_token"
    gen_perms_apply_data.assert_called_once_with(
        "system", "subject", [{"action": "action", "resources_list": [["resources"]]}]
    )
