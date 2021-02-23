# -*- coding: utf-8 -*-
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
        }
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
        }
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
            }
        ]
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
            }
        ]
    }
    assert c.convert(data) == "(id == '1' OR name == 'test')"
