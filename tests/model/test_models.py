# -*- coding: utf-8 -*-

from iam.model.models import (
    SystemProviderConfig,
    System,
    ReferenceResourceType,
    ResourceProviderConfig,
    ResourceType,
    InstanceSelection,
    RelatedResourceType,
    Action,
    ActionTopology,
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
