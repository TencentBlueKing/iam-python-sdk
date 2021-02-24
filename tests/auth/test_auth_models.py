# -*- coding: utf-8 -*-
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest

from iam.auth.models import BaseObject, Subject, Action, Resource, Request, MultiActionRequest


class BaseObjectTest(unittest.TestCase):
    """
    for abstractmethod, make sure no absent
    """

    @patch.object(BaseObject, "__abstractmethods__", set())
    def test(self):
        self.instance = BaseObject()

        self.instance.to_dict()
        self.instance.validate()


def test_subject():
    with pytest.raises(TypeError):
        Subject(1, "id").validate()

    with pytest.raises(TypeError):
        Subject("1", 2).validate()

    with pytest.raises(ValueError):
        Subject("", "1").validate()

    with pytest.raises(ValueError):
        Subject("1", "").validate()

    s = Subject("host", "1")
    assert s.type == "host"
    assert s.to_dict()["type"] == "host"
    assert s.id == "1"
    assert s.to_dict()["id"] == "1"

    with pytest.raises(AttributeError):
        s.invalidattr = "aaa"


def test_action():
    with pytest.raises(TypeError):
        Action(1).validate()

    with pytest.raises(ValueError):
        Action("").validate()

    a = Action("edit")
    assert a.id == "edit"
    assert a.to_dict()["id"] == "edit"

    with pytest.raises(AttributeError):
        a.invalidattr = "aaa"


def test_resource():
    with pytest.raises(TypeError):
        Resource(1, "type", "id", {}).validate()

    with pytest.raises(TypeError):
        Resource("system", 1, "id", {}).validate()

    with pytest.raises(TypeError):
        Resource("system", "type", 1, {}).validate()

    with pytest.raises(TypeError):
        Resource("system", "type", "id", [1, 2]).validate()

    with pytest.raises(ValueError):
        Resource("", "type", "id", {}).validate()

    with pytest.raises(ValueError):
        Resource("system", "", "id", {}).validate()

    with pytest.raises(ValueError):
        Resource("system", "type", "", {}).validate()

    r = Resource("system", "type", "id", {})
    assert r.system == "system"
    assert r.type == "type"
    assert r.id == "id"
    assert r.attribute == {}

    assert r.to_dict()["system"] == "system"

    with pytest.raises(AttributeError):
        r.invalidattr = "aaa"


def test_request():
    s = Subject("user", "tom")
    a = Action("edit")
    r = Resource("bk_paas", "app", "bk-test", {})
    rs = [r]

    # invalid
    isubject = Subject(1, "tom")
    iaction = Action(1)
    iresource = Resource("", "app", "bk-test", {})
    iresources = [iresource]

    with pytest.raises(TypeError):
        Request(1, s, a, rs, None).validate()

    with pytest.raises(TypeError):
        Request("bk_paas", 1, a, rs, None).validate()

    with pytest.raises(TypeError):
        Request("bk_paas", s, 1, rs, None).validate()

    with pytest.raises(TypeError):
        Request("bk_paas", s, a, 1, None).validate()

    with pytest.raises(TypeError):
        Request("bk_paas", s, a, rs, [1, 2]).validate()

    with pytest.raises(ValueError):
        Request("", s, a, rs, None).validate()

    # with pytest.raises(ValueError):
    #     Request("bk_paas", s, a, [], None).validate()

    with pytest.raises(ValueError):
        Request("bk_paas", isubject, a, rs, None).validate()

    with pytest.raises(ValueError):
        Request("bk_paas", s, iaction, rs, None).validate()

    # with pytest.raises(ValueError):
    #     Request("bk_paas", s, a, [], None).validate()

    with pytest.raises(ValueError):
        Request("bk_paas", s, a, iresources, None).validate()

    r = Request("bk_paas", s, a, rs, None)
    assert r.system == "bk_paas"
    assert r.subject == s
    assert r.action == a
    assert r.resources == rs
    assert r.environment is None

    assert r.to_dict()["system"] == "bk_paas"

    # hash
    r1 = Request(
        "demo",
        Subject("user", "tom"),
        Action("access_developer_center"),
        rs,
        None,
    )
    r2 = Request(
        "demo",
        Subject("user", "tom"),
        Action("access_developer_center"),
        rs,
        None,
    )
    r3 = Request(
        "demo",
        Subject("user", "tom1"),
        Action("access_developer_center"),
        rs,
        None,
    )
    assert hash(r1) == hash(r1)
    assert hash(r1) == hash(r2)
    assert hash(r1) != hash(r3)
    assert hash(r2) != hash(r3)


def test_multi_action_request():
    s = Subject("user", "tom")
    a = Action("edit")
    actions = [a]
    r = Resource("bk_paas", "app", "bk-test", {})
    rs = [r]

    # invalid
    isubject = Subject(1, "tom")
    iaction = Action(1)
    iactions = [iaction]
    iresource = Resource("", "app", "bk-test", {})
    iresources = [iresource]

    with pytest.raises(TypeError):
        MultiActionRequest(1, s, actions, rs, None).validate()

    with pytest.raises(TypeError):
        MultiActionRequest("bk_paas", 1, actions, rs, None).validate()

    with pytest.raises(TypeError):
        MultiActionRequest("bk_paas", s, 1, rs, None).validate()

    with pytest.raises(TypeError):
        MultiActionRequest("bk_paas", s, actions, 1, None).validate()

    with pytest.raises(TypeError):
        MultiActionRequest("bk_paas", s, actions, rs, [1, 2]).validate()

    with pytest.raises(ValueError):
        MultiActionRequest("", s, actions, rs, None).validate()

    with pytest.raises(ValueError):
        MultiActionRequest("bk_paas", isubject, actions, rs, None).validate()

    with pytest.raises(ValueError):
        MultiActionRequest("bk_paas", s, iactions, rs, None).validate()

    with pytest.raises(ValueError):
        MultiActionRequest("bk_paas", s, actions, iresources, None).validate()

    r = MultiActionRequest("bk_paas", s, actions, rs, None)
    assert r.system == "bk_paas"
    assert r.subject == s
    assert r.actions == actions
    assert r.resources == rs
    assert r.environment is None

    assert r.to_dict()["system"] == "bk_paas"
