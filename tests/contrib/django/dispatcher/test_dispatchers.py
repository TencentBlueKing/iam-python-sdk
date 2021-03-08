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

import json

import pytest

from iam.contrib.django.dispatcher.exceptions import KeywordTooShortException

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import patch, MagicMock

from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher, InvalidPageException
from iam.exceptions import AuthInvalidOperation
from iam.resource.provider import ListResult, ResourceProvider


def test_basic_resource_api_dispatcher_register():
    dispatcher = DjangoBasicResourceApiDispatcher("iam", "system")

    class TestResourceProvider(ResourceProvider):
        def list_attr(self, **options):
            return ListResult(results=[1, 2, 3], count=100)

        def list_attr_value(self, filter, page, **options):
            return ListResult(results=[filter, page], count=100)

        def list_instance(self, filter, page, **options):
            return ListResult(results=[filter, page], count=100)

        def fetch_instance_info(self, filter, **options):
            return ListResult(
                results=[
                    filter,
                ],
                count=100,
            )

        def list_instance_by_policy(self, filter, page, **options):
            return ListResult(results=[filter, page], count=100)

    with pytest.raises(AuthInvalidOperation):
        dispatcher.register("type", "provider")

    provider = TestResourceProvider()
    dispatcher.register("type", provider)
    assert id(provider) == id(dispatcher._provider["type"])

    with pytest.raises(AuthInvalidOperation):
        dispatcher.register("type", provider)


def test_basic_resource_api_dispatcher_as_view():
    def dec1(view):
        setattr(view, "dec1", True)
        return view

    def dec2(view):
        setattr(view, "dec2", True)
        return view

    view = DjangoBasicResourceApiDispatcher("iam", "system").as_view([dec1, dec2])
    assert view.csrf_exempt is True
    assert view.dec1 is True
    assert view.dec2 is True


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__auth_not_allowed():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=False)

    req = MagicMock()
    req.META = {"HTTP_AUTHORIZATION": "auth_token"}

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 401
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "basic auth failed"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__json_load_fail():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    req = MagicMock()
    req.body = "body"

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 400
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "reqeust body is not a valid json"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__basic_params_error():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    req = MagicMock()
    req.body = "{}"

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 400
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "method and type is required field"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__unsupport_type():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    req = MagicMock()
    req.body = json.dumps({"method": "list_attr", "type": "unsupport_type"})

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 404
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "unsupport resource type: unsupport_type"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__unsupport_method():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    req = MagicMock()
    req.body = json.dumps({"method": "unsupport_method", "type": "type"})

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")
    dispatcher._provider["type"] = "provider"

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 404
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "unsupport method: unsupport_method"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__processor_raise():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    req = MagicMock()
    req.body = json.dumps({"method": "raise", "type": "type"})

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")
    dispatcher._provider["type"] = "provider"
    dispatcher._dispatch_raise = MagicMock(side_effect=Exception("exc_token"))

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 500
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "exc_token"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__processor_raise_invalid_page():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    req = MagicMock()
    req.body = json.dumps({"method": "raise", "type": "type"})

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")
    dispatcher._provider["type"] = "provider"
    dispatcher._dispatch_raise = MagicMock(side_effect=InvalidPageException("exc_token"))

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 422
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "exc_token"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
def test_basic_resource_api_dispatcher__dispatch__processor_raise_keyword_too_short():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    req = MagicMock()
    req.body = json.dumps({"method": "raise", "type": "type"})

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")
    dispatcher._provider["type"] = "provider"
    dispatcher._dispatch_raise = MagicMock(side_effect=KeywordTooShortException("exc_token"))

    resp = dispatcher._dispatch(req)

    assert resp["code"] == 406
    assert resp["result"] is False
    assert resp["data"] is None
    assert resp["message"] == "exc_token"
    assert "X-Request-Id" in resp


@patch("iam.contrib.django.dispatcher.dispatchers.JsonResponse", dict)
@patch(
    "iam.contrib.django.dispatcher.dispatchers.get_page_obj",
    MagicMock(return_value={"limit": "limit", "offset": "offset"}),
)
def test_basic_resource_api_dispatcher__dispatch():
    iam = MagicMock()
    iam.is_basic_auth_allowed = MagicMock(return_value=True)

    dispatcher = DjangoBasicResourceApiDispatcher(iam, "system")

    class SpyResourceProvider(ResourceProvider):
        def __init__(self):
            self.list_attr_spy = {}
            self.list_attr_value_spy = {}
            self.list_instance_spy = {}
            self.fetch_instance_info_spy = {}
            self.list_instance_by_policy_spy = {}
            self.search_instance_spy = {}
            self.pre_list_attr = MagicMock()
            self.pre_list_attr_value = MagicMock()
            self.pre_list_instance = MagicMock()
            self.pre_fetch_instance_info = MagicMock()
            self.pre_list_instance_by_policy = MagicMock()
            self.pre_search_instance = MagicMock()

        def list_attr(self, **options):
            self.list_attr_spy["options"] = options
            return ListResult(results=["list_attr_token"], count=100)

        def list_attr_value(self, filter, page, **options):
            self.list_attr_value_spy["filter"] = filter
            self.list_attr_value_spy["page"] = page
            self.list_attr_value_spy["options"] = options
            return ListResult(results=["list_attr_value_token"], count=100)

        def list_instance(self, filter, page, **options):
            self.list_instance_spy["filter"] = filter
            self.list_instance_spy["page"] = page
            self.list_instance_spy["options"] = options
            return ListResult(results=["list_instance_token"], count=100)

        def fetch_instance_info(self, filter, **options):
            self.fetch_instance_info_spy["filter"] = filter
            self.fetch_instance_info_spy["options"] = options
            return ListResult(results=["fetch_instance_info_token"], count=100)

        def list_instance_by_policy(self, filter, page, **options):
            self.list_instance_by_policy_spy["filter"] = filter
            self.list_instance_by_policy_spy["page"] = page
            self.list_instance_by_policy_spy["options"] = options
            return ListResult(results=["list_instance_by_policy_token"], count=100)

        def search_instance(self, filter, page, **options):
            self.search_instance_spy["filter"] = filter
            self.search_instance_spy["page"] = page
            self.search_instance_spy["options"] = options
            return ListResult(results=["search_instance_token"], count=100)

    provider = SpyResourceProvider()
    dispatcher.register("spy", provider)

    # test list_attr
    list_attr_req = MagicMock()
    list_attr_req.body = json.dumps({"method": "list_attr", "type": "spy"})
    list_attr_req.META = {"HTTP_X_REQUEST_ID": "rid", "HTTP_BLUEKING_LANGUAGE": "en"}

    resp = dispatcher._dispatch(list_attr_req)

    provider.pre_list_attr.assert_called_once_with(language="en")
    assert resp["code"] == 0
    assert resp["result"] is True
    assert resp["data"] == ["list_attr_token"]
    assert resp["X-Request-Id"] == "rid"
    assert "message" in resp
    assert provider.list_attr_spy == {"options": {"language": "en"}}

    # test list_attr_value
    list_attr_value_req = MagicMock()
    list_attr_value_req.body = json.dumps(
        {
            "method": "list_attr_value",
            "type": "spy",
            "filter": {"attr": "attr", "keyword": "keyword", "ids": "ids"},
            "page": {"limit": "limit", "offset": "offset"},
        }
    )
    list_attr_value_req.META = {"HTTP_X_REQUEST_ID": "rid", "HTTP_BLUEKING_LANGUAGE": "en"}

    resp = dispatcher._dispatch(list_attr_value_req)

    provider.pre_list_attr_value.assert_called_once_with(
        {"attr": "attr", "keyword": "keyword", "ids": "ids"}, {"limit": "limit", "offset": "offset"}, language="en"
    )
    assert resp["code"] == 0
    assert resp["result"] is True
    assert resp["data"] == {"count": 100, "results": ["list_attr_value_token"]}
    assert resp["X-Request-Id"] == "rid"
    assert "message" in resp
    assert provider.list_attr_value_spy == {
        "options": {"language": "en"},
        "filter": {"attr": "attr", "keyword": "keyword", "ids": "ids"},
        "page": {"limit": "limit", "offset": "offset"},
    }

    # test list_instance
    list_instance_req = MagicMock()
    list_instance_req.body = json.dumps(
        {
            "method": "list_instance",
            "type": "spy",
            "filter": {"parent": "parent", "search": "search", "resource_type_chain": "resource_type_chain"},
            "page": {"limit": "limit", "offset": "offset"},
        }
    )
    list_instance_req.META = {"HTTP_X_REQUEST_ID": "rid", "HTTP_BLUEKING_LANGUAGE": "en"}

    resp = dispatcher._dispatch(list_instance_req)

    provider.pre_list_instance.assert_called_once_with(
        {"parent": "parent", "search": "search", "resource_type_chain": "resource_type_chain"},
        {"limit": "limit", "offset": "offset"},
        language="en",
    )
    assert resp["code"] == 0
    assert resp["result"] is True
    assert resp["data"] == {"count": 100, "results": ["list_instance_token"]}
    assert resp["X-Request-Id"] == "rid"
    assert "message" in resp
    assert provider.list_instance_spy == {
        "options": {"language": "en"},
        "filter": {"parent": "parent", "search": "search", "resource_type_chain": "resource_type_chain"},
        "page": {"limit": "limit", "offset": "offset"},
    }

    # test search_instance
    search_instance_req = MagicMock()
    search_instance_req.body = json.dumps(
        {
            "method": "search_instance",
            "type": "spy",
            "filter": {"parent": "parent", "keyword": "keyword"},
            "page": {"limit": "limit", "offset": "offset"},
        }
    )
    search_instance_req.META = {"HTTP_X_REQUEST_ID": "rid", "HTTP_BLUEKING_LANGUAGE": "en"}

    resp = dispatcher._dispatch(search_instance_req)

    provider.pre_search_instance.assert_called_once_with(
        {"parent": "parent", "keyword": "keyword"},
        {"limit": "limit", "offset": "offset"},
        language="en",
    )
    assert resp["code"] == 0
    assert resp["result"] is True
    assert resp["data"] == {"count": 100, "results": ["search_instance_token"]}
    assert resp["X-Request-Id"] == "rid"
    assert "message" in resp
    assert provider.search_instance_spy == {
        "options": {"language": "en"},
        "filter": {"parent": "parent", "keyword": "keyword"},
        "page": {"limit": "limit", "offset": "offset"},
    }

    # test fetch_instance_info
    fetch_instance_info_req = MagicMock()
    fetch_instance_info_req.body = json.dumps(
        {"method": "fetch_instance_info", "type": "spy", "filter": {"ids": "ids", "attrs": "attrs"}}
    )
    fetch_instance_info_req.META = {"HTTP_X_REQUEST_ID": "rid", "HTTP_BLUEKING_LANGUAGE": "en"}

    resp = dispatcher._dispatch(fetch_instance_info_req)

    provider.pre_fetch_instance_info.assert_called_once_with({"ids": "ids", "attrs": "attrs"}, language="en")
    assert resp["code"] == 0
    assert resp["result"] is True
    assert resp["data"] == ["fetch_instance_info_token"]
    assert resp["X-Request-Id"] == "rid"
    assert "message" in resp
    assert provider.fetch_instance_info_spy == {
        "options": {"language": "en"},
        "filter": {"ids": "ids", "attrs": "attrs"},
    }

    # test list_instance_by_policy
    list_instance_by_policy_req = MagicMock()
    list_instance_by_policy_req.body = json.dumps(
        {
            "method": "list_instance_by_policy",
            "type": "spy",
            "filter": {"expression": "expression"},
            "page": {"limit": "limit", "offset": "offset"},
        }
    )
    list_instance_by_policy_req.META = {"HTTP_X_REQUEST_ID": "rid", "HTTP_BLUEKING_LANGUAGE": "en"}

    resp = dispatcher._dispatch(list_instance_by_policy_req)

    provider.pre_list_instance_by_policy.assert_called_once_with(
        {"expression": "expression"}, {"limit": "limit", "offset": "offset"}, language="en"
    )
    assert resp["code"] == 0
    assert resp["result"] is True
    assert resp["data"] == ["list_instance_by_policy_token"]
    assert resp["X-Request-Id"] == "rid"
    assert "message" in resp
    assert provider.list_instance_by_policy_spy == {
        "options": {"language": "en"},
        "filter": {"expression": "expression"},
        "page": {"limit": "limit", "offset": "offset"},
    }
