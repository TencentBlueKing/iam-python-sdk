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
# import unittest
# fmt: off
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest

from iam.auth.models import Action, MultiActionRequest, Request, Resource, Subject
from iam.contrib.converter.sql import SQLConverter
from iam.eval.expression import make_expression
from iam.eval.object import ObjectSet
from iam.exceptions import AuthInvalidParam, AuthInvalidRequest
from iam.iam import IAM


def new_mock_iam():
    return IAM("test", "test", "iam_host", "paas_host")


def new_valid_request():
    return Request("test", Subject("app", "abc"), Action("edit"), [], {})


# validate
def test_iam_validate_request():
    iam = new_mock_iam()
    # invalid type
    with pytest.raises(AuthInvalidRequest):
        iam._validate_request(None)

    with pytest.raises(AuthInvalidRequest):
        iam._validate_request(1)

    # invalid value
    r = Request("test", "tom", "edit", [], {})
    with pytest.raises(TypeError):
        iam._validate_request(r)

    r = Request("test", Subject("app", "abc"), Action("edit"), [], {})
    assert iam._validate_request(r) is None


def test_iam_validate_multi_action_request():
    iam = new_mock_iam()
    # invalid type
    with pytest.raises(AuthInvalidRequest):
        iam._validate_multi_action_request(None)

    with pytest.raises(AuthInvalidRequest):
        iam._validate_multi_action_request(1)

    r = MultiActionRequest("test", "tom", "edit", [], {})
    with pytest.raises(TypeError):
        iam._validate_multi_action_request(r)

    subject = Subject("user", "admin")
    action1 = Action("flow_edit")
    r = MultiActionRequest(
        "bk_sops",
        subject,
        [action1, ],
        [],
        None
    )
    assert iam._validate_multi_action_request(r) is None


def test_iam_validate_resource_list():
    iam = new_mock_iam()

    # invalid
    with pytest.raises(AuthInvalidParam):
        iam._validate_resources_list(None)
    with pytest.raises(AuthInvalidParam):
        iam._validate_resources_list({})

    # empty
    assert iam._validate_resources_list([]) is None

    # not empty
    # wrong list
    with pytest.raises(AuthInvalidParam):
        iam._validate_resources_list([1, 2, 3]) is None
    with pytest.raises(AuthInvalidParam):
        iam._validate_resources_list([[1], [2], [3]]) is None

    # right list
    resource1 = Resource("bk_sops", "flow", "1", {})
    resources = [resource1]
    resources_list = [resources]
    assert iam._validate_resources_list(resources_list) is None


def test_iam_validate_resource_list_same_local_only():
    iam = new_mock_iam()
    resource1 = Resource("bk_sops", "flow", "1", {})

    # invalid, with resources of other system
    resource2 = Resource("bk_cmdb", "host", "1", {})
    resources = [resource1, resource2]
    resources_list = [resources]
    with pytest.raises(AuthInvalidParam):
        iam._validate_resources_list_same_local_only("bk_sops", resources_list)

    # invalid, with different type resources
    resource2 = Resource("bk_sops", "task", "2", {})
    resources = [resource1, resource2]
    resources_list = [resources]
    with pytest.raises(AuthInvalidParam):
        iam._validate_resources_list_same_local_only("bk_sops", resources_list)

    # valid
    resource2 = Resource("bk_sops", "flow", "2", {})
    resources = [resource1, resource2]
    resources_list = [resources]
    assert iam._validate_resources_list_same_local_only("bk_sops", resources_list) is None


# eval
def test_eval_policy():
    iam = new_mock_iam()
    # no policies
    obj_set = ObjectSet()
    assert not iam._eval_policy(None, obj_set)
    assert not iam._eval_policy([], obj_set)
    assert not iam._eval_policy({}, obj_set)

    # any
    policy = {
        "op": "any",
        "field": "aaa",
        "value": ""
    }
    assert iam._eval_policy(policy, obj_set)


def test_eval_expr():
    iam = new_mock_iam()
    policy = {
        "op": "any",
        "field": "aaa",
        "value": ""
    }
    expr = make_expression(policy)
    obj_set = ObjectSet()

    assert iam._eval_expr(expr, obj_set)


# main funcs
def test_is_allowed():
    # any
    with patch.object(IAM, "_do_policy_query", return_value={"op": "any", "field": "", "value": ""}):
        r = new_valid_request()
        iam = new_mock_iam()
        assert iam.is_allowed(r)


def test_is_allowed_with_cache():
    # any
    iam = new_mock_iam()
    r = new_valid_request()
    with patch.object(IAM, "_do_policy_query", return_value={"op": "any", "field": "", "value": ""}):
        assert iam.is_allowed_with_cache(r)
        assert iam.is_allowed_with_cache(r)

    # without mock, has cache
    assert iam.is_allowed_with_cache(r)

    # without mock, different isinstance, also cache
    iam2 = new_mock_iam()
    r2 = new_valid_request()
    assert iam2.is_allowed_with_cache(r2)


def test_is_allowed_with_policy_cache():
    # any
    iam = new_mock_iam()
    r = new_valid_request()
    with patch.object(IAM, "_do_policy_query", return_value={"op": "any", "field": "", "value": ""}):
        assert iam.is_allowed_with_cache(r)
        assert iam.is_allowed_with_cache(r)

    # without mock, has cache
    assert iam.is_allowed_with_cache(r)

    # without mock, different isinstance, also cache
    iam2 = new_mock_iam()
    r2 = new_valid_request()
    assert iam2.is_allowed_with_cache(r2)


def test_batch_is_allowed():
    # any
    with patch.object(IAM, "_do_policy_query", return_value={"op": "any", "field": "", "value": ""}):
        r = new_valid_request()
        iam = new_mock_iam()

        resource1 = Resource("test", "flow", "1", {})
        resource2 = Resource("test", "flow", "2", {})
        resources_list = [[resource1], [resource2]]

        result = iam.batch_is_allowed(r, resources_list)
        assert "1" in result and result["1"]
        assert "2" in result and result["2"]


def test_resource_multi_actions_allowed():
    # any
    data = [{"condition": {"field": "flow.id", "value": [], "op": "any"}, "action": {"id": "flow_edit"}},
            {"condition": {"field": "flow.id", "value": [], "op": "any"}, "action": {"id": "flow_view"}},
            {"condition": None, "action": {"id": "flow_delete"}}]
    with patch.object(IAM, "_do_policy_query_by_actions", return_value=data):
        subject = Subject("user", "admin")
        action1 = Action("flow_edit")
        action2 = Action("flow_view")
        action3 = Action("flow_delete")
        resource1 = Resource("bk_sops", "flow", "1", {})

        r = MultiActionRequest(
            "bk_sops",
            subject,
            [action1, action2, action3],
            [resource1],
            None
        )

        iam = new_mock_iam()

        result = iam.resource_multi_actions_allowed(r)
        # {'flow_edit': True, 'flow_view': True, 'flow_delete': False}
        assert "flow_edit" in result and result["flow_edit"]
        assert "flow_view" in result and result["flow_view"]
        assert "flow_delete" in result and (not result["flow_delete"])


def test_batch_resource_multi_actions_allowed():
    # any
    data = [{"condition": {"field": "flow.id", "value": [], "op": "any"}, "action": {"id": "flow_edit"}},
            {"condition": {"field": "flow.id", "value": [], "op": "any"}, "action": {"id": "flow_view"}},
            {"condition": None, "action": {"id": "flow_delete"}}]
    with patch.object(IAM, "_do_policy_query_by_actions", return_value=data):
        subject = Subject("user", "admin")
        action1 = Action("flow_edit")
        action2 = Action("flow_view")
        action3 = Action("flow_delete")
        resource1 = Resource("bk_sops", "flow", "1", {})
        resource2 = Resource("bk_sops", "flow", "2", {})
        resource3 = Resource("bk_sops", "flow", "3", {})

        r = MultiActionRequest(
            "bk_sops",
            subject,
            [action1, action2, action3],
            [],
            None
        )

        iam = new_mock_iam()

        result = iam.batch_resource_multi_actions_allowed(r, [[resource1], [resource2], [resource3]])
        # {'1': {'flow_edit': True, 'flow_view': True, 'flow_delete': False},
        # '2': {'flow_edit': True, 'flow_view': True, 'flow_delete': False},
        # '3': {'flow_edit': True, 'flow_view': True, 'flow_delete': False}}
        assert len(result) == 3
        assert "1" in result
        assert "2" in result
        assert "3" in result

        assert result["1"]["flow_edit"]
        assert result["1"]["flow_view"]
        assert not result["1"]["flow_delete"]


def test_make_filter():
    r = new_valid_request()

    # any
    with patch.object(IAM, "_do_policy_query", return_value={"op": "any", "field": "", "value": ""}):
        iam = new_mock_iam()
        sql = iam.make_filter(r, SQLConverter, {})

        assert sql == "1 == 1"

    data = {
        "op": "OR",
        "content": [
            {
                "op": "eq",
                "field": "host.id",
                "value": "hello"
            },
            {
                "op": "not_eq",
                "field": "host.label",
                "value": ["db", "redis"]
            }
        ]
    }
    with patch.object(IAM, "_do_policy_query", return_value=data):
        iam = new_mock_iam()
        sql = iam.make_filter(r, SQLConverter, {"host.label": "tag"})

        assert sql == "(host.id == 'hello' OR (tag != 'db' AND tag != 'redis'))"


def test_query_subjects():
    pass


def test_get_token():
    pass


def test_get_apply_url():
    pass


def test_grant_resource_creator_actions():
    pass


def test_is_basic_auth_allowed():
    with patch.object(IAM, "get_token", return_value=(True, "", "abc")):
        iam = new_mock_iam()
        assert iam.is_basic_auth_allowed("test", "Basic YmtfaWFtOmFiYw==")
# fmt: on
