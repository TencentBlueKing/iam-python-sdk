# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云-权限中心Python SDK(iam-python-sdk) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

# description
should support both python2 and python3

表达式求值 demo

DONE:
1. 实现 and/or
2. 实现所有类型的操作符
3. 实现递归求值
4. 加入模板方法限制, 确保每个operator实现eval
5. 加入Enum类, 去除字面量
"""

from __future__ import print_function

import logging
import sys

from iam import IAM, Action, DictObject, ObjectSet, Request, Resource, Subject, make_expression

iam_logger = logging.getLogger("iam")
iam_logger.setLevel(logging.DEBUG)

debug_hanler = logging.StreamHandler(sys.stdout)
debug_hanler.setFormatter(logging.Formatter("[IAM] %(asctime)s %(message)s"))
iam_logger.addHandler(debug_hanler)
iam_logger.propagate = True


def print_spearator():
    print("================================================")


def eval_exmaple():
    # create a resource, type is host
    h = {"id": "hello"}
    host = DictObject(h)
    print("host.id =", host.id)
    print("host.notexists =", host.notexists)

    # create a resource, type is module
    class Module(object):
        pass

    m = Module()
    m.id = "world"

    module = DictObject(m)
    print("module.id =", module.id)
    print("module.notexists =", module.notexists)

    print_spearator()

    # make a object set contains two resource type
    s = ObjectSet()
    s.add_object("host", host)
    s.add_object("module", module)

    print("object_set host.id", s.get("host.id"))
    print("object_set host.id", s.get("host.notexists"))
    print("object_set module.id", s.get("module.id"))
    print("object_set module.id", s.get("module.notexists"))
    print("object_set cluster.id", s.get("cluster.id"))

    print_spearator()

    # define a policy
    data = {
        "op": "OR",
        "content": [
            {"op": "eq", "field": "host.id", "value": "hello"},
            {"op": "not_eq", "field": "module.id", "value": "world"},
        ],
    }
    # make a policy expression
    expr = make_expression(data)
    print("the expression:", expr.expr())
    print("the expression render:", expr.render(s))
    print("the eval result:", expr.eval(s))

    print_spearator()

    data1 = {
        "op": "eq",
        "field": "host.id",
        "value": "hello",
    }
    expr1 = make_expression(data1)
    print("the expression:", expr1.expr())
    print("the expression render:", expr1.render(s))
    print("the eval result:", expr1.eval(s))

    print_spearator()

    data1 = {
        "op": "not_eq",
        "field": "host.id",
        "value": "hello",
    }
    expr1 = make_expression(data1)
    print("the expression:", expr1.expr())
    print("the expression render:", expr1.render(s))
    print("the eval result:", expr1.eval(s))


def convert_example():
    data = {
        "op": "OR",
        "content": [
            {"op": "eq", "field": "host.id", "value": "hello"},
            {"op": "not_eq", "field": "host.label", "value": ["db", "redis"]},
        ],
    }

    # sql expression
    from iam.contrib.converter.sql import SQLConverter

    expr = make_expression(data)
    print("the expression:", expr.expr())
    s = SQLConverter()
    print("to sql where: ", s.convert(data))

    print_spearator()

    # django expression
    from iam.contrib.converter.queryset import DjangoQuerySetConverter

    s = DjangoQuerySetConverter()
    expr = make_expression(data)
    print("the expression:", expr.expr())
    print("to django queryset:", s.convert(data))


if __name__ == "__main__":
    # eval
    print("\nTHE EVAL EXAMPLE:\n")
    eval_exmaple()

    print_spearator()

    # convert to sql / django queryset
    print("\nTHE CONVERT EXAMPLE:\n")
    convert_example()

    # make a request
    print_spearator()

    subject = Subject("user", "admin")
    # action = Action("edit_app")
    # action = Action("access_developer_center")
    action = Action("develop_app")
    resource = Resource("bk_paas", "app", "bk_test", {})

    request = Request("bk_paas", subject, action, [resource], None)

    print("the request: ", request.to_dict())

    iam = IAM("bk_paas", "2353e89a-10a2-4f30-9f6b-8973e9cd1404", "http://127.0.0.1:8080", "https://{PAAS_DOMAIN}")
    # recommend if got an APIGateway
    # iam = IAM("bk_paas", "2353e89a-10a2-4f30-9f6b-8973e9cd1404", bk_apigateway_url="http://{IAM_APIGATEWAY_URL}")
    # 多租户用户需要传入bk_tenant_id
    # iam = IAM("bk_paas", "2353e89a-10a2-4f30-9f6b-8973e9cd1404", bk_apigateway_url="http://{IAM_APIGATEWAY_URL}", bk_tenant_id="{your bk_tenant_id}")
    print("is_allowed: ", iam.is_allowed(request))
    print("query: ", iam.make_filter(request))
