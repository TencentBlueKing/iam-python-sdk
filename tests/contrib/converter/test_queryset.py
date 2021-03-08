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

from django.db.models import Q

from iam import DjangoQuerySetConverter


def assertQEqual(q1, q2):
    assert str(q1) == str(q2)


def test_eq():
    c = DjangoQuerySetConverter()

    assertQEqual(c._eq("id", "1"), Q(id="1"))
    assertQEqual(c._eq("id", 1), Q(id=1))
    assertQEqual(c._eq("id", ["1", 1]), (Q(id="1") | Q(id=1)))


def test_not_eq():
    c = DjangoQuerySetConverter()

    assertQEqual(c._not_eq("id", "1"), ~Q(id="1"))
    assertQEqual(c._not_eq("id", 1), ~Q(id=1))
    assertQEqual(c._not_eq("id", ["1", 1]), (~Q(id="1") & ~Q(id=1)))


def test_in():
    c = DjangoQuerySetConverter()

    assertQEqual(c._in("id", ["1"]), Q(id__in=["1"]))
    assertQEqual(c._in("id", ["1", "2"]), Q(id__in=["1", "2"]))

    assertQEqual(c._in("id", [1, 2]), Q(id__in=[1, 2]))


def test_not_in():
    c = DjangoQuerySetConverter()

    assertQEqual(c._not_in("id", ["1"]), ~Q(id__in=["1"]))
    assertQEqual(c._not_in("id", ["1", "2"]), ~Q(id__in=["1", "2"]))

    assertQEqual(c._not_in("id", [1, 2]), ~Q(id__in=[1, 2]))


def test_contains():
    c = DjangoQuerySetConverter()

    assertQEqual(c._contains("id", "1"), Q(id__contains="1"))
    assertQEqual(c._contains("id", 1), Q(id__contains=1))
    assertQEqual(c._contains("id", ["1", 1]), (Q(id__contains="1") | Q(id__contains=1)))


def test_not_contains():
    c = DjangoQuerySetConverter()

    assertQEqual(c._not_contains("id", "1"), ~Q(id__contains="1"))
    assertQEqual(c._not_contains("id", 1), ~Q(id__contains=1))
    assertQEqual(c._not_contains("id", ["1", 1]), (~Q(id__contains="1") & ~Q(id__contains=1)))


def test_starts_with():
    c = DjangoQuerySetConverter()

    assertQEqual(c._starts_with("id", "test"), Q(id__startswith="test"))
    assertQEqual(c._starts_with("id", ["test", "test1"]), (Q(id__startswith="test") | Q(id__startswith="test1")))

    assertQEqual(c._starts_with("id", ["test", 123]), (Q(id__startswith="test") | Q(id__startswith=123)))


def test_not_starts_with():
    c = DjangoQuerySetConverter()

    assertQEqual(c._not_starts_with("id", "test"), ~Q(id__startswith="test"))
    assertQEqual(c._not_starts_with("id", ["test", "test1"]), (~Q(id__startswith="test") & ~Q(id__startswith="test1")))

    assertQEqual(c._not_starts_with("id", ["test", 123]), (~Q(id__startswith="test") & ~Q(id__startswith=123)))


def test_ends_with():
    c = DjangoQuerySetConverter()

    assertQEqual(c._ends_with("id", "test"), Q(id__endswith="test"))
    assertQEqual(c._ends_with("id", ["test", "test1"]), (Q(id__endswith="test") | Q(id__endswith="test1")))

    assertQEqual(c._ends_with("id", ["test", 123]), (Q(id__endswith="test") | Q(id__endswith=123)))


def test_not_ends_with():
    c = DjangoQuerySetConverter()

    assertQEqual(c._not_ends_with("id", "test"), ~Q(id__endswith="test"))
    assertQEqual(c._not_ends_with("id", ["test", "test1"]), (~Q(id__endswith="test") & ~Q(id__endswith="test1")))

    assertQEqual(c._not_ends_with("id", ["test", 123]), (~Q(id__endswith="test") & ~Q(id__endswith=123)))


def test_lt():
    c = DjangoQuerySetConverter()

    assertQEqual(c._lt("id", "1"), Q(id__lt="1"))
    assertQEqual(c._lt("id", 1), Q(id__lt=1))
    assertQEqual(c._lt("id", ["1", 1]), (Q(id__lt="1") | Q(id__lt=1)))


def test_lte():
    c = DjangoQuerySetConverter()

    assertQEqual(c._lte("id", "1"), Q(id__lte="1"))
    assertQEqual(c._lte("id", 1), Q(id__lte=1))
    assertQEqual(c._lte("id", ["1", 1]), (Q(id__lte="1") | Q(id__lte=1)))


def test_gt():
    c = DjangoQuerySetConverter()

    assertQEqual(c._gt("id", "1"), Q(id__gt="1"))
    assertQEqual(c._gt("id", 1), Q(id__gt=1))
    assertQEqual(c._gt("id", ["1", 1]), (Q(id__gt="1") | Q(id__gt=1)))


def test_gte():
    c = DjangoQuerySetConverter()

    assertQEqual(c._gte("id", "1"), Q(id__gte="1"))
    assertQEqual(c._gte("id", 1), Q(id__gte=1))
    assertQEqual(c._gte("id", ["1", 1]), (Q(id__gte="1") | Q(id__gte=1)))


def test_any():
    c = DjangoQuerySetConverter()

    assertQEqual(c._any(1, 1), ~Q(pk=None))


def test_and():
    c = DjangoQuerySetConverter()

    content = [{"op": "eq", "field": "id", "value": "1"}, {"op": "eq", "field": "name", "value": "test"}]
    assertQEqual(c._and(content), (Q(id="1") & Q(name="test")))


def test_or():
    c = DjangoQuerySetConverter()

    content = [{"op": "eq", "field": "id", "value": "1"}, {"op": "eq", "field": "name", "value": "test"}]
    assertQEqual(c._or(content), (Q(id="1") | Q(name="test")))


def test_convert():
    c = DjangoQuerySetConverter()

    data = {
        "op": "AND",
        "content": [{"op": "eq", "field": "id", "value": "1"}, {"op": "eq", "field": "name", "value": "test"}],
    }
    assertQEqual(c.convert(data), (Q(id="1") & Q(name="test")))

    data = {
        "op": "OR",
        "content": [{"op": "eq", "field": "id", "value": "1"}, {"op": "eq", "field": "name", "value": "test"}],
    }
    assertQEqual(c.convert(data), (Q(id="1") | Q(name="test")))


def test_value_hooks():
    def hook(value):
        assert value == "1"
        return "new_value"

    c = DjangoQuerySetConverter(value_hooks={"id": hook})

    data = {
        "op": "AND",
        "content": [{"op": "eq", "field": "id", "value": "1"}, {"op": "eq", "field": "name", "value": "test"}],
    }
    assertQEqual(c.convert(data), (Q(id="new_value") & Q(name="test")))

    # invalid hook
    hook = "invalid hook"
    c = DjangoQuerySetConverter(value_hooks={"id": hook})

    data = {
        "op": "AND",
        "content": [{"op": "eq", "field": "id", "value": "1"}, {"op": "eq", "field": "name", "value": "test"}],
    }
    assertQEqual(c.convert(data), (Q(id="1") & Q(name="test")))


def test_operator_map():
    class TestOpMapConverter(DjangoQuerySetConverter):
        def operator_map(self, operator, field, value):
            if operator == "eq":
                assert field == "name"
                assert value == "test"
                return self._starts_with

    data = {
        "op": "AND",
        "content": [{"op": "lt", "field": "id", "value": "1"}, {"op": "eq", "field": "name", "value": "test"}],
    }
    c = TestOpMapConverter()
    assertQEqual(c.convert(data), (Q(id__lt="1") & Q(name__startswith="test")))
