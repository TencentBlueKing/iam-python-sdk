# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - 权限中心 Python SDK(iam-python-sdk) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from iam.api.client import Client


def _test_ok_message_data(mock_request, call_func):
    # 1. request fail
    mock_request.return_value = (False, "error", {})
    ok, message, data = call_func({})

    assert not ok

    # 2. request success, code not 0
    mock_request.return_value = (True, "error status_code != 200", {"code": 404, "message": "not found"})
    ok, message, data = call_func({})
    assert not ok

    # 3. request success, code 0
    mock_request.return_value = (True, "ok", {"code": 0, "message": "ok", "data": {1: 1}})
    ok, message, data = call_func({})
    assert ok
    assert message == "ok"
    assert data
    assert data[1] == 1


def _test_v2_ok_message_data(mock_request, call_func):
    # 1. request fail
    mock_request.return_value = (False, "error", {})
    ok, message, data = call_func("system", {})

    assert not ok

    # 2. request success, code not 0
    mock_request.return_value = (True, "error status_code != 200", {"code": 404, "message": "not found"})
    ok, message, data = call_func("system", {})
    assert not ok

    # 3. request success, code 0
    mock_request.return_value = (True, "ok", {"code": 0, "message": "ok", "data": {1: 1}})
    ok, message, data = call_func("system", {})
    assert ok
    assert message == "ok"
    assert data
    assert data[1] == 1


@patch("iam.api.client.http_post")
def test_client_policy_query(mock_post):
    c = Client("bk_paas", "", "http://127.0.0.1:1234")

    _test_ok_message_data(mock_post, c.policy_query)

    _test_ok_message_data(mock_post, c.policy_query_by_actions)


@patch("iam.api.client.http_post")
def test_v2_client_policy_query(mock_post):
    c = Client("bk_paas", "", "http://127.0.0.1:1234")

    _test_v2_ok_message_data(mock_post, c.v2_policy_query)

    _test_v2_ok_message_data(mock_post, c.v2_policy_query_by_actions)


def _test_ok_message(mock_request, call_func, kwargs):
    # 1. request fail
    mock_request.return_value = (False, "error", {})
    ok, message = call_func(**kwargs)

    assert not ok

    # 2. request success, code not 0
    mock_request.return_value = (True, "error status_code != 200", {"code": 404, "message": "not found"})
    ok, message = call_func(**kwargs)
    assert not ok

    # 3. request success, code 0
    mock_request.return_value = (True, "ok", {"code": 0, "message": "ok", "data": {1: 1}})
    ok, message = call_func(**kwargs)
    assert ok
    assert message == "ok"


@patch("iam.api.client.http_post")
def test_create(mock_post):
    c = Client("bk_paas", "", "http://127.0.0.1:1234")

    _test_ok_message(mock_post, c.add_system, dict(data={}))

    _test_ok_message(mock_post, c.batch_add_resource_types, dict(system_id="bk_paas", data={}))

    _test_ok_message(mock_post, c.batch_add_actions, dict(system_id="bk_paas", data={}))

    _test_ok_message(mock_post, c.add_action_topology, dict(system_id="bk_paas", action_type=None, data={}))


@patch("iam.api.client.http_put")
def test_update(mock_put):
    c = Client("bk_paas", "", "http://127.0.0.1:1234")

    _test_ok_message(mock_put, c.update_system, dict(system_id="", data={}))

    _test_ok_message(mock_put, c.update_resource_type, dict(system_id="bk_paas", resource_type_id="", data={}))

    _test_ok_message(mock_put, c.update_action, dict(system_id="bk_paas", action_id="", data={}))

    _test_ok_message(mock_put, c.update_action_topology, dict(system_id="bk_paas", action_type=None, data={}))


@patch("iam.api.client.http_delete")
def test_delete(mock_delete):
    c = Client("bk_paas", "", "http://127.0.0.1:1234")

    _test_ok_message(mock_delete, c.batch_delete_resource_types, dict(system_id="", data={}))

    _test_ok_message(mock_delete, c.batch_delete_actions, dict(system_id="", data={}))


@patch.dict(os.environ, {"ABC": "true"})
def test_client_extra_url_params_empty():
    c = Client("bk_paas", "", "http://127.0.0.1:1234")
    assert not c._extra_url_params


@patch.dict(os.environ, {"IAM_API_DEBUG": "true"})
def test_client_extra_url_params_debug_1():
    c = Client("bk_paas", "", "http://127.0.0.1:1234")
    assert c._extra_url_params
    assert len(c._extra_url_params) == 1
    assert c._extra_url_params.get("debug") == "true"


@patch.dict(os.environ, {"BKAPP_IAM_API_DEBUG": "true"})
def test_client_extra_url_params_debug_2():
    c = Client("bk_paas", "", "http://127.0.0.1:1234")
    assert c._extra_url_params
    assert len(c._extra_url_params) == 1
    assert c._extra_url_params.get("debug") == "true"


@patch.dict(os.environ, {"IAM_API_FORCE": "true"})
def test_client_extra_url_params_force_1():
    c = Client("bk_paas", "", "http://127.0.0.1:1234")
    assert c._extra_url_params
    assert len(c._extra_url_params) == 1
    assert c._extra_url_params.get("force") == "true"


@patch.dict(os.environ, {"BKAPP_IAM_API_FORCE": "true"})
def test_client_extra_url_params_force_2():
    c = Client("bk_paas", "", "http://127.0.0.1:1234")
    assert c._extra_url_params
    assert len(c._extra_url_params) == 1
    assert c._extra_url_params.get("force") == "true"
