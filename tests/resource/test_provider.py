# -*- coding: utf-8 -*-

from iam.resource.provider import ListResult


def test_list_result():
    lr = ListResult([1, 2, 3], count=100)

    assert lr.count == 100
    assert lr.to_dict() == {"count": 100, "results": [1, 2, 3]}
    assert lr.to_list() == [1, 2, 3]
