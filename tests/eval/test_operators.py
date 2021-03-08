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
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from iam import (
    OP,
    AndOperator,
    AnyOperator,
    BinaryOperator,
    ContainsOperator,
    EndsWithOperator,
    EqualOperator,
    GTEOperator,
    GTOperator,
    InOperator,
    LogicalOperator,
    LTEOperator,
    LTOperator,
    NotContainsOperator,
    NotEndsWithOperator,
    NotEqualOperator,
    NotInOperator,
    NotStartsWithOperator,
    ObjectSet,
    Operator,
    OrOperator,
    StartsWithOperator,
)


# =========== base operators
class BaseOperatorTest(unittest.TestCase):
    """
    for abstractmethod, make sure no absent
    """

    @patch.object(Operator, "__abstractmethods__", set())
    def test(self):
        self.instance = Operator("test")

        self.instance.expr()
        assert str(self.instance) == "operator:test"


class BaseLogicalOperatorTest(unittest.TestCase):
    """
    for abstractmethod, make sure no absent
    """

    @patch.object(LogicalOperator, "__abstractmethods__", set())
    def test(self):
        self.instance = LogicalOperator("AND", [EqualOperator("host.id", "1"), NotEqualOperator("host.path", "2")])

        self.instance.eval(None)

        assert self.instance.expr() == "((host.id eq '1') AND (host.path not_eq '2'))"
        os = ObjectSet()
        os.add_object("host", {"id": "1", "path": "2"})
        assert self.instance.render(os) == "(('1' eq '1') AND ('2' not_eq '2'))"


class BaseBinaryOperatorTest(unittest.TestCase):
    """
    for abstractmethod, make sure no absent
    """

    @patch.object(BinaryOperator, "__abstractmethods__", set())
    def test(self):
        self.instance = BinaryOperator("eq", "host.id", "1")

        assert self.instance.expr() == "(host.id eq '1')"
        os = ObjectSet()
        os.add_object(
            "host",
            {
                "id": "1",
            },
        )
        assert self.instance.render(os) == "('1' eq '1')"

        self.instance.calculate(1, 1)


# =========== binary operator _eval_positive and _eval_negative

# TODO: 1 positive

# TODO: 2 negative


# =========== binary operators
def test_equal_operator():
    eq = EqualOperator("host.id", "localhost")

    # the __repr__
    assert str(eq) == "operator:eq"

    assert eq.op == OP.EQ
    assert eq.expr() == "(host.id eq 'localhost')"

    d1 = ObjectSet()
    d1.add_object("host", {"id": "localhost"})
    assert eq.eval(d1)

    d2 = ObjectSet()
    d2.add_object("host", {"id": "remote"})
    assert not eq.eval(d2)

    # TODO: add some more case?
    d3 = ObjectSet()
    d3.add_object("host", {"id": 1})
    assert not eq.eval(d3)


def test_not_equal_operator():
    not_eq = NotEqualOperator("host.id", "localhost")

    assert not_eq.op == OP.NOT_EQ
    assert not_eq.expr() == "(host.id not_eq 'localhost')"

    d1 = ObjectSet()
    d1.add_object("host", {"id": "localhost"})
    assert not not_eq.eval(d1)

    d2 = ObjectSet()
    d2.add_object("host", {"id": "remote"})
    assert not_eq.eval(d2)

    # TODO: add some more case?
    # d3 = ObjectSet()
    # d3.add_object("host", {
    #     "id": 1
    # })
    # assert not not_eq.eval(d3)


def test_in_operator():
    d1 = ObjectSet()
    d1.add_object(
        "host",
        {
            "id": "a1",
        },
    )
    d2 = ObjectSet()
    d2.add_object(
        "host",
        {
            "id": "a2",
        },
    )

    # IN
    inop = InOperator("host.id", ["a1", "a3"])

    assert inop.op == OP.IN
    assert inop.expr() == "(host.id in ['a1', 'a3'])"

    assert inop.eval(d1)
    assert not inop.eval(d2)

    # NOT_IN
    notinop = NotInOperator("host.id", ["a1", "a3"])

    assert notinop.op == OP.NOT_IN
    assert notinop.expr() == "(host.id not_in ['a1', 'a3'])"

    assert not notinop.eval(d1)
    assert notinop.eval(d2)

    # attr is a list
    # common: a3
    d3 = ObjectSet()
    d3.add_object(
        "host",
        {
            "id": ["a4", "a3"],
        },
    )
    assert inop.eval(d3)
    assert not notinop.eval(d3)

    # no common
    d4 = ObjectSet()
    d4.add_object(
        "host",
        {
            "id": ["b1", "b2"],
        },
    )
    assert not inop.eval(d4)
    assert notinop.eval(d4)


def test_contains_operator():
    d1 = ObjectSet()
    d1.add_object(
        "host",
        {
            "owner": ["a1", "a3"],
        },
    )
    d2 = ObjectSet()
    d2.add_object(
        "host",
        {
            "owner": ["a2"],
        },
    )

    # CONTAINS
    c = ContainsOperator("host.owner", "a1")

    assert c.op == OP.CONTAINS
    assert c.expr() == "(host.owner contains 'a1')"

    assert c.eval(d1)
    assert not c.eval(d2)

    # NOT_CONTAINS
    nc = NotContainsOperator("host.owner", "a1")

    assert nc.op == OP.NOT_CONTAINS
    assert nc.expr() == "(host.owner not_contains 'a1')"

    assert not nc.eval(d1)
    assert nc.eval(d2)

    # value is a list
    c1 = ContainsOperator("host.owner", ["a1", "a2"])
    nc1 = NotContainsOperator("host.owner", ["a1", "a2"])

    d3 = ObjectSet()
    d3.add_object("host", {"owner": ["a3", "a2"]})

    assert c1.eval(d3)
    assert not nc1.eval(d3)

    d4 = ObjectSet()
    d4.add_object("host", {"owner": ["b1", "b2"]})
    assert not c1.eval(d4)
    assert nc1.eval(d4)


def test_text_operator():
    d1 = ObjectSet()
    d1.add_object(
        "person",
        {
            "name": "hello",
        },
    )
    d2 = ObjectSet()
    d2.add_object(
        "person",
        {
            "name": "world",
        },
    )
    # STARTS_WITH
    sw = StartsWithOperator("person.name", "hel")

    assert sw.op == OP.STARTS_WITH
    assert sw.expr() == "(person.name starts_with 'hel')"

    assert sw.eval(d1)
    assert not sw.eval(d2)

    # NOT_STARTS_WITH
    nsw = NotStartsWithOperator("person.name", "hel")

    assert nsw.op == OP.NOT_STARTS_WITH
    assert nsw.expr() == "(person.name not_starts_with 'hel')"

    assert not nsw.eval(d1)
    assert nsw.eval(d2)

    # ENDS_WITH
    ew = EndsWithOperator("person.name", "llo")

    assert ew.op == OP.ENDS_WITH
    assert ew.expr() == "(person.name ends_with 'llo')"

    assert ew.eval(d1)
    assert not ew.eval(d2)

    # NOT_ENDS_WITH
    new = NotEndsWithOperator("person.name", "llo")

    assert new.op == OP.NOT_ENDS_WITH
    assert new.expr() == "(person.name not_ends_with 'llo')"

    assert not new.eval(d1)
    assert new.eval(d2)


def test_math_operator():
    d1 = ObjectSet()
    d1.add_object(
        "person",
        {
            "age": 19,
        },
    )
    d2 = ObjectSet()
    d2.add_object(
        "person",
        {
            "age": 20,
        },
    )
    d3 = ObjectSet()
    d3.add_object(
        "person",
        {
            "age": 21,
        },
    )

    # LT
    lt = LTOperator("person.age", 20)

    assert lt.op == OP.LT
    assert lt.expr() == "(person.age lt 20)"

    assert lt.eval(d1)
    assert not lt.eval(d2)
    assert not lt.eval(d3)

    # LTE
    lte = LTEOperator("person.age", 20)

    assert lte.op == OP.LTE
    assert lte.expr() == "(person.age lte 20)"

    assert lte.eval(d1)
    assert lte.eval(d2)
    assert not lte.eval(d3)

    # GT
    gt = GTOperator("person.age", 20)

    assert gt.op == OP.GT
    assert gt.expr() == "(person.age gt 20)"

    assert not gt.eval(d1)
    assert not gt.eval(d2)
    assert gt.eval(d3)

    # GTE
    gte = GTEOperator("person.age", 20)

    assert gte.op == OP.GTE
    assert gte.expr() == "(person.age gte 20)"

    assert not gte.eval(d1)
    assert gte.eval(d2)
    assert gte.eval(d3)


def test_any_operator():
    a = AnyOperator("host.id", "localhost")

    assert a.op == OP.ANY
    assert a.expr() == "(host.id any 'localhost')"

    d1 = ObjectSet()
    d1.add_object("host", {"id": "localhost"})
    assert a.eval(d1)

    d2 = ObjectSet()
    d2.add_object("host", {"id": "remote"})
    assert a.eval(d2)

    d3 = ObjectSet()
    d3.add_object("host", {"id": 1})
    assert a.eval(d3)


def test_binary_operator_eval_positive():
    """
    op = eq => one of attr equals one of value

    attr = 1; value = 1; True
    attr = 1; value = [1, 2]; True
    attr = [1, 2]; value = 2; True
    attr = [1, 2]; value = [5, 1]; True

    attr = [1, 2]; value = [3, 4]; False
    """
    d1 = ObjectSet()
    d1.add_object(
        "host",
        {
            "id": 1,
        },
    )
    d2 = ObjectSet()
    d2.add_object(
        "host",
        {
            "id": [1, 2],
        },
    )

    eq1 = EqualOperator("host.id", 1)
    assert eq1.eval(d1)

    eq2 = EqualOperator("host.id", [1, 2])
    assert eq2.eval(d1)

    eq3 = EqualOperator("host.id", 2)
    assert eq3.eval(d2)

    eq4 = EqualOperator("host.id", [5, 1])
    assert eq4.eval(d2)

    eq5 = EqualOperator("host.id", [3, 4])
    assert not eq5.eval(d2)

    # IN
    d3 = ObjectSet()
    d3.add_object(
        "host",
        {
            "id": [1, 2],
        },
    )
    # one of [1,2] in [2, 4]
    eq6 = InOperator("host.id", [2, 4])
    assert eq6.eval(d3)

    # CONTAINS
    d4 = ObjectSet()
    d4.add_object(
        "host",
        {
            "id": [1, 2],
        },
    )
    # [1, 2] contains 1 of [2,4]
    eq6 = ContainsOperator("host.id", [2, 4])
    assert eq6.eval(d4)


def test_binary_operator_eval_negative():
    d1 = ObjectSet()
    d1.add_object(
        "host",
        {
            "id": 1,
        },
    )
    d2 = ObjectSet()
    d2.add_object(
        "host",
        {
            "id": [1, 2],
        },
    )

    neq1 = NotEqualOperator("host.id", 2)
    assert neq1.eval(d1)

    neq2 = NotEqualOperator("host.id", [2])
    assert neq2.eval(d1)

    neq3 = NotEqualOperator("host.id", [3, 4])
    assert neq3.eval(d2)

    neq4 = NotEqualOperator("host.id", 3)
    assert neq4.eval(d2)

    neq5 = NotEqualOperator("host.id", [2, 3])
    assert not neq5.eval(d2)

    # NOT_IN
    d3 = ObjectSet()
    d3.add_object(
        "host",
        {
            "id": [1, 2],
        },
    )
    # all of [1,2] not in [3,4]
    eq6 = NotInOperator("host.id", [3, 4])
    assert eq6.eval(d3)

    # NOT_CONTAINS
    d4 = ObjectSet()
    d4.add_object(
        "host",
        {
            "id": [1, 2],
        },
    )
    # [1,2] not contains all of [3,4]
    eq6 = NotContainsOperator("host.id", [3, 4])
    assert eq6.eval(d4)


# =========== logical operators
def test_logical_operator():
    d1 = ObjectSet()
    d1.add_object("host", {"id": "a1", "name": "b1"})

    d2 = ObjectSet()
    d2.add_object("host", {"id": "a1", "name": "c1"})

    d3 = ObjectSet()
    d3.add_object("host", {"id": "a2", "name": "c1"})

    eq1 = EqualOperator("host.id", "a1")
    eq2 = EqualOperator("host.name", "b1")

    # AND
    andop = AndOperator([eq1, eq2])

    assert andop.op == OP.AND
    assert andop.expr() == "((host.id eq 'a1') AND (host.name eq 'b1'))"

    assert andop.eval(d1)
    assert not andop.eval(d2)

    # OR
    orop = OrOperator([eq1, eq2])
    assert orop.op == OP.OR
    assert orop.expr() == "((host.id eq 'a1') OR (host.name eq 'b1'))"

    assert orop.eval(d1)
    assert orop.eval(d2)
    assert not orop.eval(d3)
