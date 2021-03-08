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

# try:
#     from unittest.mock import patch
# except ImportError:
#     from mock import patch

# import pytest

from iam import meta


def test_setup_system():
    meta.setup_system("s1", "sn1")
    meta.setup_system("s2", "sn2")
    assert meta.get_system_name("s1") == "sn1"
    assert meta.get_system_name("s2") == "sn2"
    assert meta.get_system_name("s3") is None


def test_setup_resource():
    meta.setup_resource("s1", "r1", "rn1")
    meta.setup_resource("s1", "r2", "rn2")
    meta.setup_resource("s2", "r1", "_rn1")
    meta.setup_resource("s2", "r3", "rn3")

    assert meta.get_resource_name("s1", "r1") == "rn1"
    assert meta.get_resource_name("s1", "r2") == "rn2"
    assert meta.get_resource_name("s2", "r1") == "_rn1"
    assert meta.get_resource_name("s2", "r3") == "rn3"
    assert meta.get_resource_name("s2", "r4") is None
    assert meta.get_resource_name("s3", "r5") is None


def test_setup_action():
    meta.setup_action("s1", "a1", "an1")
    meta.setup_action("s1", "a2", "an2")
    meta.setup_action("s2", "a1", "_an1")
    meta.setup_action("s2", "a3", "an3")

    assert meta.get_action_name("s1", "a1") == "an1"
    assert meta.get_action_name("s1", "a2") == "an2"
    assert meta.get_action_name("s2", "a1") == "_an1"
    assert meta.get_action_name("s2", "a3") == "an3"
    assert meta.get_action_name("s2", "a4") is None
    assert meta.get_action_name("s3", "a5") is None
