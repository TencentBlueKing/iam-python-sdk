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

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

# import pytest

from iam import Action, Resource, Subject, utils


def test_gen_perms_apply_data():
    system = "test_system"
    subject = Subject("user", "admin")
    action1 = Action("action1")
    action2 = Action("action2")
    action3 = Action("action3")
    action4 = Action("action4")

    resource1 = Resource("test_system", "r1", "r1id", {"name": "r1n"})
    resource2 = Resource("test_system", "r2", "r2id", None)
    resource3 = Resource("test_system", "r3", "r3id", {})
    resource4 = Resource("another_system", "r4", "r4id", {"name": "r4n"})
    resource5 = Resource("another_system", "r4", "r5id", {"name": "r5n"})
    resource6 = Resource("test_system", "r6", "r6id", {"name": "r6n", "_bk_iam_path_": "/biz,1/set,2/module,3/"})

    def get_system_name(system):
        return {"test_system": "test_system_name", "another_system": "another_system_name"}[system]

    def get_action_name(system, action):
        return {
            "test_system": {
                "action1": "action1_name",
                "action2": "action2_name",
                "action3": "action3_name",
                "action4": "action4_name",
            }
        }[system][action]

    def get_resource_name(system, resource):
        return {
            "test_system": {
                "r1": "r1_type",
                "r2": "r2_type",
                "r3": "r3_type",
                "r6": "r6_type",
                "biz": "biz_type",
                "set": "set_type",
                "module": "module_type",
            },
            "another_system": {"r4": "r4_type"},
        }[system][resource]

    with patch("iam.utils.meta.get_system_name", MagicMock(side_effect=get_system_name)):
        with patch("iam.utils.meta.get_action_name", MagicMock(side_effect=get_action_name)):
            with patch("iam.utils.meta.get_resource_name", MagicMock(side_effect=get_resource_name)):
                data = utils.gen_perms_apply_data(
                    system,
                    subject,
                    [
                        {"action": action1, "resources_list": [[resource1, resource2, resource3, resource4]]},
                        {"action": action2, "resources_list": [[]]},
                        {
                            "action": action3,
                            "resources_list": [
                                [resource1, resource3, resource4],
                                [resource1, resource3, resource4],
                                [resource2, resource3, resource5],
                            ],
                        },
                        {"action": action4, "resources_list": [[resource6]]},
                    ],
                )

                # assert data
    # TODO: fix dict compare
    assert data == {
        "system_id": "test_system",
        "system_name": "test_system_name",
        "actions": [
            {
                "id": "action1",
                "name": "action1_name",
                "related_resource_types": [
                    {
                        "system_id": "test_system",
                        "system_name": "test_system_name",
                        "type": "r3",
                        "type_name": "r3_type",
                        "instances": [
                            [{"type": "r1", "type_name": "r1_type", "id": "r1id", "name": "r1n"}],
                            [{"type": "r2", "type_name": "r2_type", "id": "r2id", "name": ""}],
                            [{"type": "r3", "type_name": "r3_type", "id": "r3id", "name": ""}],
                        ],
                    },
                    {
                        "system_id": "another_system",
                        "system_name": "another_system_name",
                        "type": "r4",
                        "type_name": "r4_type",
                        "instances": [[{"type": "r4", "type_name": "r4_type", "id": "r4id", "name": "r4n"}]],
                    },
                ],
            },
            {"id": "action2", "name": "action2_name", "related_resource_types": []},
            {
                "id": "action3",
                "name": "action3_name",
                "related_resource_types": [
                    {
                        "system_id": "test_system",
                        "system_name": "test_system_name",
                        "type": "r3",
                        "type_name": "r3_type",
                        "instances": [
                            [{"type": "r1", "type_name": "r1_type", "id": "r1id", "name": "r1n"}],
                            [{"type": "r3", "type_name": "r3_type", "id": "r3id", "name": ""}],
                            [{"type": "r1", "type_name": "r1_type", "id": "r1id", "name": "r1n"}],
                            [{"type": "r3", "type_name": "r3_type", "id": "r3id", "name": ""}],
                            [{"type": "r2", "type_name": "r2_type", "id": "r2id", "name": ""}],
                            [{"type": "r3", "type_name": "r3_type", "id": "r3id", "name": ""}],
                        ],
                    },
                    {
                        "system_id": "another_system",
                        "system_name": "another_system_name",
                        "type": "r4",
                        "type_name": "r4_type",
                        "instances": [
                            [{"type": "r4", "type_name": "r4_type", "id": "r4id", "name": "r4n"}],
                            [{"type": "r4", "type_name": "r4_type", "id": "r4id", "name": "r4n"}],
                            [{"type": "r4", "type_name": "r4_type", "id": "r5id", "name": "r5n"}],
                        ],
                    },
                ],
            },
            {
                "id": "action4",
                "name": "action4_name",
                "related_resource_types": [
                    {
                        "system_id": "test_system",
                        "system_name": "test_system_name",
                        "type": "r6",
                        "type_name": "r6_type",
                        "instances": [
                            [
                                {"type": "biz", "type_name": "biz_type", "id": "1", "name": "biz,1"},
                                {"type": "set", "type_name": "set_type", "id": "2", "name": "set,2"},
                                {"type": "module", "type_name": "module_type", "id": "3", "name": "module,3"},
                                {"type": "r6", "type_name": "r6_type", "id": "r6id", "name": "r6n"},
                            ]
                        ],
                    }
                ],
            },
        ],
    }
