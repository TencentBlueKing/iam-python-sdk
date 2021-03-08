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
import pytest

from iam import SQLConverter


def test_to_str_present():
    c = SQLConverter()

    assert c._to_str_present(1, True) == 1
    assert c._to_str_present("1", True) == "'1'"
    assert c._to_str_present("1", False) == "1"


def test_eq():
    c = SQLConverter()

    assert c._eq("id", "1") == "id == '1'"
    assert c._eq("id", 1) == "id == 1"

    assert c._eq("id", ["1", 1]) == "(id == '1' OR id == 1)"


def test_not_eq():
    c = SQLConverter()

    assert c._not_eq("id", "1") == "id != '1'"
    assert c._not_eq("id", 1) == "id != 1"

    assert c._not_eq("id", ["1", 1]) == "(id != '1' AND id != 1)"


def test_in():
    c = SQLConverter()

    assert c._in("id", ["1"]) == "id IN ('1')"
    assert c._in("id", ["1", "2"]) == "id IN ('1','2')"

    assert c._in("id", [1, 2]) == "id IN (1,2)"


def test_not_in():
    c = SQLConverter()

    assert c._not_in("id", ["1"]) == "id NOT IN ('1')"
    assert c._not_in("id", ["1", "2"]) == "id NOT IN ('1','2')"

    assert c._not_in("id", [1, 2]) == "id NOT IN (1,2)"


def test_contains():
    c = SQLConverter()

    with pytest.raises(NotImplementedError):
        c._contains("1", "1")


def test_not_contains():
    c = SQLConverter()

    with pytest.raises(NotImplementedError):
        c._not_contains("1", "1")


def test_starts_with():
    c = SQLConverter()

    assert c._starts_with("id", "test") == "id LIKE 'test%'"
    assert c._starts_with("id", ["test", "test1"]) == "(id LIKE 'test%' OR id LIKE 'test1%')"
    assert c._starts_with("id", ["test", 123]) == "(id LIKE 'test%' OR id LIKE '123%')"


def test_not_starts_with():
    c = SQLConverter()

    assert c._not_starts_with("id", "test") == "id NOT LIKE 'test%'"
    assert c._not_starts_with("id", ["test", "test1"]) == "(id NOT LIKE 'test%' AND id NOT LIKE 'test1%')"
    assert c._not_starts_with("id", ["test", 123]) == "(id NOT LIKE 'test%' AND id NOT LIKE '123%')"


def test_ends_with():
    c = SQLConverter()

    assert c._ends_with("id", "test") == "id LIKE '%test'"
    assert c._ends_with("id", ["test", "test1"]) == "(id LIKE '%test' OR id LIKE '%test1')"
    assert c._ends_with("id", ["test", 123]) == "(id LIKE '%test' OR id LIKE '%123')"


def test_not_ends_with():
    c = SQLConverter()

    assert c._not_ends_with("id", "test") == "id NOT LIKE '%test'"
    assert c._not_ends_with("id", ["test", "test1"]) == "(id NOT LIKE '%test' AND id NOT LIKE '%test1')"
    assert c._not_ends_with("id", ["test", 123]) == "(id NOT LIKE '%test' AND id NOT LIKE '%123')"


def test_lt():
    c = SQLConverter()

    assert c._lt("id", "1") == "id < '1'"
    assert c._lt("id", 1) == "id < 1"

    assert c._lt("id", ["1", 1]) == "(id < '1' OR id < 1)"


def test_lte():
    c = SQLConverter()

    assert c._lte("id", "1") == "id <= '1'"
    assert c._lte("id", 1) == "id <= 1"

    assert c._lte("id", ["1", 1]) == "(id <= '1' OR id <= 1)"


def test_gt():
    c = SQLConverter()

    assert c._gt("id", "1") == "id > '1'"
    assert c._gt("id", 1) == "id > 1"

    assert c._gt("id", ["1", 1]) == "(id > '1' OR id > 1)"


def test_gte():
    c = SQLConverter()

    assert c._gte("id", "1") == "id >= '1'"
    assert c._gte("id", 1) == "id >= 1"

    assert c._gte("id", ["1", 1]) == "(id >= '1' OR id >= 1)"


def test_any():
    c = SQLConverter()

    assert c._any(1, 1) == "1 == 1"


def test_and():
    c = SQLConverter()

    content = [
        {
            "op": "eq",
            "field": "id",
            "value": "1",
        },
        {
            "op": "eq",
            "field": "name",
            "value": "test",
        },
    ]
    assert c._and(content) == "(id == '1' AND name == 'test')"


def test_or():
    c = SQLConverter()

    content = [
        {
            "op": "eq",
            "field": "id",
            "value": "1",
        },
        {
            "op": "eq",
            "field": "name",
            "value": "test",
        },
    ]
    assert c._or(content) == "(id == '1' OR name == 'test')"


def test_convert():
    c = SQLConverter()

    data = {
        "op": "AND",
        "content": [
            {
                "op": "eq",
                "field": "id",
                "value": "1",
            },
            {
                "op": "eq",
                "field": "name",
                "value": "test",
            },
        ],
    }
    assert c.convert(data) == "(id == '1' AND name == 'test')"

    data = {
        "op": "OR",
        "content": [
            {
                "op": "eq",
                "field": "id",
                "value": "1",
            },
            {
                "op": "eq",
                "field": "name",
                "value": "test",
            },
        ],
    }
    assert c.convert(data) == "(id == '1' OR name == 'test')"
