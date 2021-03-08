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
import sys

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock


sys.modules["tastypie.exceptions"] = MagicMock()
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response_for_resources_list  # noqa
from iam.exceptions import MultiAuthFailedException  # noqa


class Resource:
    def __init__(self, rid):
        self.id = rid


def test_allow_or_raise_immediate_response_for_resources_list__allowed():
    system = "system"
    subject = "subject"
    action = "action"
    resources = [[Resource("r1")], [Resource("r2")]]

    iam = MagicMock()
    iam.batch_is_allowed = MagicMock(return_value={"r1": True, "r2": True})

    Request = MagicMock()

    with patch("iam.contrib.tastypie.shortcuts.Request", Request):
        allow_or_raise_immediate_response_for_resources_list(iam, system, subject, action, resources)

    Request.assert_called_once_with(system, subject, action, [], None)


def test_allow_or_raise_immediate_response_for_resources_list__raise():
    system = "system"
    subject = "subject"
    action = "action"
    resources = [[Resource("r1")], [Resource("r2")]]

    iam = MagicMock()
    iam.batch_is_allowed = MagicMock(return_value={"r1": True, "r2": False})
    not_allowed_resources_list = [resources[1]]

    Request = MagicMock()

    with patch("iam.contrib.tastypie.shortcuts.Request", Request):
        try:
            allow_or_raise_immediate_response_for_resources_list(iam, system, subject, action, resources)
        except MultiAuthFailedException as e:
            assert e.system == system
            assert e.subject == subject
            assert e.action == action
            assert e.resources_list == not_allowed_resources_list
        else:
            assert False, "allow_or_raise_auth_failed did not raise"

    Request.assert_called_once_with(system, subject, action, [], None)
