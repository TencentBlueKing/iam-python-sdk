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
"""

from iam.model.models import (
    Action,
    ActionTopology,
    InstanceSelection,
    ReferenceResourceType,
    RelatedResourceType,
    ResourceProviderConfig,
    ResourceType,
    System,
    SystemProviderConfig,
)


def test_models():
    spc = SystemProviderConfig("host", "basic")

    System("test", "test", "test", "", "", "", spc)

    rrt = ReferenceResourceType("test", "app")

    ResourceProviderConfig("/api/v1/resources")

    ResourceType("app", "app", "app", "", "", None, spc, 1)

    InstanceSelection("", "", [rrt])

    RelatedResourceType("test", "a", "a", "a", None, None, None)

    Action("edit", "edit", "edit", "", "", "create", None, None, 1)

    ActionTopology("create", [], [])
