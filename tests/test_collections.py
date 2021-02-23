# -*- coding: utf-8 -*-

import pytest

from iam.collection import FancyDict


def test_fancy_dict():
    d = FancyDict()
    d.a = "1"
    assert "1" == d.a
    assert "1" == d["a"]

    with pytest.raises(AttributeError):
        d.b
