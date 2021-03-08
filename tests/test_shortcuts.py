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
# import pytest
# import unittest

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import patch, MagicMock

from iam.exceptions import AuthFailedException
from iam.shortcuts import allow_or_raise_auth_failed


def test_allow_or_raise_auth_failed__allowed():
    system = "system"
    subject = "subject"
    action = "action"
    resources = ["r1", "r2"]

    iam = MagicMock()
    iam.is_allowed = MagicMock(return_value=True)

    Request = MagicMock()

    with patch("iam.shortcuts.Request", Request):
        allow_or_raise_auth_failed(iam, system, subject, action, resources)

    Request.assert_called_once_with(system, subject, action, resources, None)


def test_allow_or_raise_auth_failed__raise():
    system = "system"
    subject = "subject"
    action = "action"
    resources = ["r1", "r2"]

    iam = MagicMock()
    iam.is_allowed = MagicMock(return_value=False)

    Request = MagicMock()

    with patch("iam.shortcuts.Request", Request):
        try:
            allow_or_raise_auth_failed(iam, system, subject, action, resources)
        except AuthFailedException as e:
            assert e.system == system
            assert e.subject == subject
            assert e.action == action
            assert e.resources == resources
        else:
            assert False, "allow_or_raise_auth_failed did not raise"

    Request.assert_called_once_with(system, subject, action, resources, None)
