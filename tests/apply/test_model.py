# -*- coding: utf-8 -*-

import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest

from iam.apply.models import (
    ActionWithoutResources,
    ActionWithResources,
    Application,
    BaseAction,
    RelatedResourceType,
    ResourceInstance,
    ResourceNode,
)


def test_resource_node():
    n = ResourceNode("app", "test", "test")
    assert n.to_dict()["type"] == "app"
    assert n.to_dict()["id"] == "test"
    assert n.to_dict()["name"] == "test"


def test_resource_instance():
    ri = ResourceInstance("")

    with pytest.raises(ValueError):
        ri.validate()

    ri = ResourceInstance("aaa")
    with pytest.raises(TypeError):
        ri.validate()

    n = ResourceNode("app", "test", "test")
    ri = ResourceInstance([n])

    valid = True
    try:
        ri.validate()
    except Exception:
        valid = False

    assert valid
    assert len(ri.to_dict()) == 1


def test_related_resource_type():
    rrt = RelatedResourceType("bk_paas", "app", "aa")
    with pytest.raises(TypeError):
        rrt.validate()

    n = ResourceNode("app", "test", "test")
    ri = ResourceInstance([n])
    rrt = RelatedResourceType("bk_paas", "app", [ri])

    valid = True
    try:
        rrt.validate()
    except Exception:
        valid = False

    assert valid
    assert rrt.to_dict()["system_id"] == "bk_paas"


class BaseActionTest(unittest.TestCase):
    """
    for abstractmethod, make sure no absent
    """

    @patch.object(BaseAction, "__abstractmethods__", set())
    def test(self):
        self.instance = BaseAction("edit")

        self.instance.to_dict()
        self.instance.validate()


def test_action_without_resources():
    a = ActionWithoutResources("edit")
    a.validate()

    assert a.to_dict()["id"] == "edit"
    assert len(a.to_dict()["related_resource_types"]) == 0


def test_action_with_resources():
    a = ActionWithResources("edit", "")

    with pytest.raises(ValueError):
        a.validate()

    a = ActionWithResources("edit", "aa")

    with pytest.raises(TypeError):
        a.validate()

    n = ResourceNode("app", "test", "test")
    ri = ResourceInstance([n])
    rrt = RelatedResourceType("bk_paas", "app", [ri])
    a = ActionWithResources("edit", [rrt])

    valid = True
    try:
        a.validate()
    except Exception:
        valid = False

    assert valid

    assert a.to_dict()["id"] == "edit"


def test_application():
    a = Application("bk_paas", "")
    with pytest.raises(ValueError):
        a.validate()

    a = Application("bk_paas", "aa")
    with pytest.raises(TypeError):
        a.validate()

    n = ResourceNode("app", "test", "test")
    ri = ResourceInstance([n])
    rrt = RelatedResourceType("bk_paas", "app", [ri])
    awr = ActionWithResources("edit", [rrt])

    a = Application("bk_paas", [awr])

    valid = True
    try:
        a.validate()
    except Exception:
        valid = False

    assert valid
