# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS
Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import pytest

# import unittest

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import patch, MagicMock

from iam.exceptions import AuthAPIError, AuthBaseException, AuthFailedException, AuthInvalidParam, AuthInvalidRequest


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
