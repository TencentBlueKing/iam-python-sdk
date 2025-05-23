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


import base64
import logging
import sys
import time
from copy import deepcopy

from cachetools import TTLCache, cached
from six import string_types

from .api.client import Client
from .apply.models import Application
from .auth.models import ApiAuthRequest, ApiBatchAuthRequest, MultiActionRequest, Request, Resource
from .cache import hash_key
from .contrib.converter.queryset import DjangoQuerySetConverter
from .eval.expression import make_expression
from .eval.object import ObjectSet
from .exceptions import AuthAPIError, AuthInvalidParam, AuthInvalidRequest

logger = logging.getLogger("iam")


class IAM(object):
    """
    input: object
    """

    def __init__(self, app_code, app_secret, bk_apigateway_url, bk_tenant_id="", api_version="v2"):
        self._client = Client(app_code, app_secret, bk_apigateway_url, bk_tenant_id)

        self._api_version = api_version

    def _do_policy_query(self, request, with_resources=True):
        data = request.to_dict()
        logger.debug("the request: %s", data)

        # NOTE: 不向服务端传任何 resource, 用于统一类资源的批量鉴权
        # 将会返回所有策略，然后遍历资源列表和策略列表，逐一计算
        if not with_resources:
            data["resources"] = []

        if self._api_version == "v2":
            ok, message, policies = self._client.v2_policy_query(request.system, data)
        else:
            ok, message, policies = self._client.policy_query(data)
        if not ok:
            raise AuthAPIError(message)
        return policies

    @cached(cache=TTLCache(maxsize=1024, ttl=60), key=hash_key)
    def _do_policy_query_with_cache(self, request):
        return self._do_policy_query(request)

    def _do_policy_query_by_actions(self, request, with_resources=True):
        data = request.to_dict()
        logger.debug("the request: %s", data)

        # NOTE: 不向服务端传任何 resource, 用于统一类资源的批量鉴权
        # 将会返回所有策略，然后遍历资源列表和策略列表，逐一计算
        if not with_resources:
            data["resources"] = []

        if self._api_version == "v2":
            ok, message, action_policies = self._client.v2_policy_query_by_actions(request.system, data)
        else:
            ok, message, action_policies = self._client.policy_query_by_actions(data)
        if not ok:
            raise AuthAPIError(message)
        return action_policies

    def _eval_expr(self, expr, obj_set):
        logger.debug("the return expr: %s", expr.expr())
        logger.debug("the return expr render: %s", expr.render(obj_set))

        # 5. eval and return
        eval_begin = time.time()
        allowed = expr.eval(obj_set)
        logger.debug("the return expr eval: %s", allowed)
        eval_time = int((time.time() - eval_begin) * 1000)
        logger.debug("the return expr eval took %s ms", eval_time)
        return allowed

    def _eval_policy(self, policy, obj_set):
        if not policy:
            return False

        expr = make_expression(policy)

        return self._eval_expr(expr, obj_set)

    def _build_object_set(self, system, resources, only_local=False):
        obj_set = ObjectSet()

        resource_id_list = []

        # if no resources or resources is None
        if not resources:
            return obj_set, ""

        for resource in resources:
            # only local resource need to be calculated
            # 跨系统资源依赖的策略在服务端就计算完了，策略表达式中只会存在本系统的
            if only_local and (resource.system != system):
                continue

            attrs = resource.attribute
            attrs["id"] = resource.id
            obj_set.add_object(resource.type, attrs)

            resource_id_list.append((resource.type, resource.id))

        # 如果只有一个本地资源，直接返回不带类型的 ID;
        # [("flow", "1")]   => "1"
        # 如果存在层级资源 返回 {type},{id}/{type2},{id2}
        # [("cluster", "a"), ("area", "b")) =>  "cluster,a/area,b"

        # NOTE: 这里不会存在=> 跨系统资源依赖=>上面已经过滤掉了
        # [("job", "script", "a"), ("cmdb", "host", "b")) =>  "job:script,a/cmdb:host,b"

        resource_id = ""
        if len(resource_id_list) == 1:
            resource_id = resource_id_list[0][1]
        else:
            resource_id = "/".join(["%s,%s" % (a[0], a[1]) for a in resource_id_list])

        return obj_set, resource_id

    def _validate_request(self, request):
        if not isinstance(request, Request):
            raise AuthInvalidRequest("request should be instance of iam.auth.models.Request")

        request.validate()

    def _validate_multi_action_request(self, request):
        if not isinstance(request, MultiActionRequest):
            raise AuthInvalidRequest("request should be instance of iam.auth.models.MultiActionRequest")

        request.validate()

    def _validate_resources_list(self, resources_list):
        # resources_list = [resources] = [[Resource], [Resource]]
        if not isinstance(resources_list, list):
            raise AuthInvalidParam("resources_list should be list of [iam.auth.models.Resource]")

        if not all([isinstance(r, list) for r in resources_list]):
            raise AuthInvalidParam("resources_list should be list of [iam.auth.models.Resource]")

        if not all([isinstance(i, Resource) for r in resources_list for i in r]):
            raise AuthInvalidParam("resources should be list of iam.auth.models.Resource")

    def _validate_resources_list_same_local_only(self, system, resources_list):
        # 校验，resources_list 中只能是本地同一类的资源
        resource_types = {}
        for rs in resources_list:
            for r in rs:
                if system != r.system:
                    raise AuthInvalidParam(
                        "resources_list not support auth for resource belong other system: %s" % r.system
                    )
                resource_types[r.type] = 1

        if len(resource_types) != 1:
            raise AuthInvalidParam(
                "resources_list should all with the same resource_type, but got %s" % resource_types.keys()
            )

    @cached(cache=TTLCache(maxsize=1024, ttl=10), key=hash_key)
    def is_allowed_with_cache(self, request):
        return self.is_allowed(request)

    def is_allowed(self, request):
        """
        单个资源是否有权限校验
        request 中会带 resource 到 IAM, IAM 会进行两阶段计算，即 resources 也会参与到计算中

        支持：
        - 本地资源 resources 中只有本地资源
        - 跨系统资源依赖 resources 中有本地也有远程资源 (此时 resoruces 一定要传，因为需要 IAM 帮助获取跨系统资源)
        """
        logger.debug("calling IAM.is_allowed(request)......")

        # 1. validate
        self._validate_request(request)

        # 2. _client.policy_query
        policies = self._do_policy_query(request)

        logger.debug("the return policies: %s", policies)
        if not policies:
            logger.debug("no return policies, will return False")
            return False

        # 3. make objSet
        obj_set, _ = self._build_object_set(request.system, request.resources, only_local=True)

        # 4. eval
        allowed = self._eval_policy(policies, obj_set)
        return allowed

    def is_allowed_with_policy_cache(self, request):
        """
        单个资源是否有权限校验，缓存查询得到的策略
        同一个 subject-system-action 查询到的策略会被缓存
        不同的实例使用同一份缓存的策略，提升鉴权性能

        策略缓存 1 分钟
        """
        # 1. validate
        self._validate_request(request)

        # 2. request without resources
        request_without_resources = deepcopy(request)
        request_without_resources.resources = []

        # 3. query policy from iam or cache
        policies = self._do_policy_query_with_cache(request_without_resources)

        logger.debug("the return policies: %s", policies)
        if not policies:
            logger.debug("no return policies, will return False")
            return False

        # 4. make objSet
        obj_set, _ = self._build_object_set(request.system, request.resources, only_local=True)

        # 5. eval
        allowed = self._eval_policy(policies, obj_set)
        return allowed

    def batch_is_allowed(self, request, resources_list):
        """
        多个资源是否有权限校验
        request 中不会带 resource 到 IAM, IAM 不会会进行两阶段计算，直接返回 system+action+subejct 的所有策略
        然后逐一计算

        - 一次策略查询，多次计算

        支持：
        - 本地资源 resources 中只有本地资源
        - **不支持**跨系统资源依赖
        """
        logger.debug("calling IAM.batch_is_allowed(request, resources_list)......")

        # 1. validate
        self._validate_request(request)
        self._validate_resources_list(resources_list)
        self._validate_resources_list_same_local_only(request.system, resources_list)

        # 2. _client.policy_query
        data = request.to_dict()
        logger.debug("the request: %s", data)

        # NOTE: 不向服务端传任何 resource
        result = {}
        policies = self._do_policy_query(request, with_resources=False)
        logger.debug("the return policies: %s", policies)
        if not policies:
            logger.debug("no return policies, will return False")
            for resources in resources_list:
                _, resource_id = self._build_object_set(request.system, resources, only_local=False)
                result[resource_id] = False

            return result

        expr = make_expression(policies)

        # 4. make objSet
        for resources in resources_list:
            obj_set, resource_id = self._build_object_set(request.system, resources, only_local=False)

            allowed = self._eval_expr(expr, obj_set)
            result[resource_id] = allowed

        return result

    def resource_multi_actions_allowed(self, request):
        """
        单个资源多个 action 是否有权限校验
        request 中会带 resource 到 IAM, IAM 会进行两阶段计算，即 resources 也会参与到计算中

        支持：
        - 本地资源 resources 中只有本地资源
        - 跨系统资源依赖 resources 中有本地也有远程资源 (此时 resoruces 一定要传，因为需要 IAM 帮助获取跨系统资源)
        """
        logger.debug("calling IAM.resource_multi_actions_allowed(request)......")

        # 1. validate
        self._validate_multi_action_request(request)

        data = request.to_dict()
        logger.debug("the request: %s", data)
        # 2. _client.policy_query_by_actions
        action_policies = self._do_policy_query_by_actions(request)

        actions_allowed = {}
        logger.debug("the return policies: %s", action_policies)
        if not action_policies:
            logger.debug("no return policies, will reject all perms")
            for a in request.to_dict()["actions"]:
                action = a["id"]
                actions_allowed[action] = False
            return actions_allowed

        # 3. calculate perms
        obj_set, _ = self._build_object_set(request.system, request.resources, only_local=True)

        # 4. 一个策略是一个表达式，计算一次
        for action_policy in action_policies:
            action = action_policy["action"]["id"]
            policies = action_policy["condition"]
            actions_allowed[action] = self._eval_policy(policies, obj_set)

        return actions_allowed

    def batch_resource_multi_actions_allowed(self, request, resources_list):
        """
        批量资源多个 action 是否有权限校验
        request 中会带 resource 到 IAM, IAM 会进行两阶段计算，即 resources 也会参与到计算中

        支持：
        - 本地资源 resources 中只有本地资源
        - **不支持**跨系统资源依赖
        """
        logger.debug("calling IAM.batch_resource_multi_actions_allowed(request, resources_list)......")

        # 1. validate
        self._validate_multi_action_request(request)
        self._validate_resources_list(resources_list)
        self._validate_resources_list_same_local_only(request.system, resources_list)

        data = request.to_dict()
        logger.debug("the request: %s", data)

        # 2. _client.policy_query_by_actions
        # NOTE: 不向服务端传任何 resource
        action_policies = self._do_policy_query_by_actions(request, with_resources=False)

        resources_actions_perms = {}

        logger.debug("the return policies: %s", action_policies)
        if not action_policies:
            logger.debug("no return policies, will reject all perms")
            for resource in resources_list:
                for a in data["actions"]:
                    action = a["id"]
                    resources_actions_perms.setdefault(resource.id, {})[action] = False
            return resources_actions_perms

        # 4. calculate perms
        for resources in resources_list:
            # NOTE: 这里假设 resources 里面只有一个本地资源
            obj_set, resource_id = self._build_object_set(request.system, resources, only_local=False)
            # FIXME: 未来这里会支持同一个系统的不同资源，届时怎么表示？

            # 一个策略是一个表达式，计算一次
            for action_policy in action_policies:
                action = action_policy["action"]["id"]
                policies = action_policy["condition"]

                resources_actions_perms.setdefault(resource_id, {})[action] = False
                resources_actions_perms[resource_id][action] = self._eval_policy(policies, obj_set)

        return resources_actions_perms

    def make_filter(self, request, converter_class=DjangoQuerySetConverter, key_mapping=None):
        logger.debug("calling IAM.make_filter(request)......")

        # 1. validate
        if not isinstance(request, Request):
            raise AuthInvalidRequest("request should be instance of iam.auth.models.Request")

        request.validate()

        # 2. _client.policy_query
        policies = self._do_policy_query(request)

        # the polices maybe none
        logger.debug("the return policies: %s", policies)
        if not policies:
            return None

        # 3. make converter
        c = converter_class(key_mapping)

        # 4. do convert and return
        converted_filters = c.convert(policies)
        logger.debug("the converted filters: %s", converted_filters)
        return converted_filters

    # TODO: add the register model apis
    def get_token(self, system):
        """获取 token
        return bool, message, token
        """
        return self._client.get_token(system)

    def is_basic_auth_allowed(self, system, basic_auth):
        logger.debug("calling IAM.is_basic_auth_allowed(basic_aut)......")

        if not isinstance(system, string_types):
            raise AuthInvalidParam("system should be a string")

        if not isinstance(basic_auth, string_types):
            raise AuthInvalidParam("basic_auth should be a string")

        auth = basic_auth.strip().split()
        if len(auth) != 2 or auth[0].lower() != "basic":
            logger.error("invalid basic auth format [length=%d, authorization=%s]", len(auth), auth)
            return False

        decoded_str = base64.b64decode(auth[1])

        if sys.version_info[0] >= 3:
            if not isinstance(decoded_str, str):
                decoded_str = decoded_str.decode()

        username, password = decoded_str.split(":")
        if username != "bk_iam":
            logger.error("username is not bk_iam")
            return False

        ok, message, token = self.get_token(system)
        if not ok:
            logger.error("get system token fail: %s", message)
            return False

        if password != token:
            logger.error(
                "password in basic_auth not equals to system token [password=%s***, token=%s***]",
                password[6:],
                token[6:],
            )
            return False

        return True

    def get_apply_url(self, application):
        if isinstance(application, dict):
            data = application
        elif isinstance(application, Application):
            # do validate
            application.validate()
            data = application.to_dict()
        else:
            raise AuthInvalidRequest("application shuld be instance of dict or iam.apply.modles.Application")

        # bool, message, url
        return self._client.get_apply_url(data)

    def grant_resource_creator_actions(self, application):
        if isinstance(application, dict):
            data = application
        else:
            raise AuthInvalidRequest("application should be instance of dict")

        # bool, message, url
        return self._client.grant_resource_creator_actions(data)

    def grant_resource_creator_action_attributes(self, application):
        if isinstance(application, dict):
            data = application
        else:
            raise AuthInvalidRequest("application should be instance of dict")

        # bool, message
        return self._client.grant_resource_creator_action_attributes(data)

    def grant_batch_resource_creator_actions(self, application):
        if isinstance(application, dict):
            data = application
        else:
            raise AuthInvalidRequest("application should be instance of dict")

        # bool, message, url
        return self._client.grant_batch_resource_creator_actions(data)

    def grant_or_revoke_instance_permission(self, request):
        if not isinstance(request, ApiAuthRequest):
            raise AuthInvalidRequest("request should be a instance of iam.auth.models.ApiAuthRequest")

        self._validate_request(request)
        data = request.to_dict()

        logger.debug("the request: %s", data)

        ok, message, policies = self._client.instance_authorization(data)
        if not ok:
            raise AuthAPIError(message)
        return policies

    def grant_or_revoke_path_permission(self, request):
        if not isinstance(request, ApiAuthRequest):
            raise AuthInvalidRequest("request should be a instance of iam.auth.models.ApiAuthRequest")
        self._validate_request(request)
        data = request.to_dict()

        logger.debug("the request: %s", data)

        ok, message, policies = self._client.path_authorization(data)
        if not ok:
            raise AuthAPIError(message)
        return policies

    def batch_grant_or_revoke_instance_permission(self, request):
        if not isinstance(request, ApiBatchAuthRequest):
            raise AuthInvalidRequest("request should be a instance of iam.auth.models.ApiBatchAuthRequest")

        self._validate_request(request)
        data = request.to_dict()

        logger.debug("the request: %s", data)

        ok, message, policies = self._client.batch_instance_authorization(data)
        if not ok:
            raise AuthAPIError(message)
        return policies

    def batch_grant_or_revoke_path_permission(self, request):
        if not isinstance(request, ApiBatchAuthRequest):
            raise AuthInvalidRequest("request should be a instance of iam.auth.models.ApiBatchAuthRequest")

        self._validate_request(request)
        data = request.to_dict()

        logger.debug("the request: %s", data)

        ok, message, policies = self._client.batch_path_authorization(data)
        if not ok:
            raise AuthAPIError(message)
        return policies

    def query_polices_with_action_id(self, system, data):

        logger.debug("calling IAM.query_polices_with_action_id.....")

        if not isinstance(system, string_types):
            raise AuthInvalidParam("system should be a string")

        if not isinstance(data, dict):
            raise AuthInvalidParam("data should be a dict")

        ok, message, policies = self._client.query_policies_with_action_id(system, data)
        if not ok:
            raise AuthAPIError(message)

        return policies
