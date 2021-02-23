# -*- coding: utf-8 -*-

from iam.resource import utils


def test_get_filter_obj():
    filter_data = {"k1": "v1", "k2": "v2"}

    filter_obj = utils.get_filter_obj(filter_data, ["k1", "k2"])
    assert filter_obj.k1 == "v1"
    assert filter_obj.k2 == "v2"

    # test filter data is empty
    filter_data = {}
    filter_obj = utils.get_filter_obj(filter_data, ["k1", "k2"])
    assert filter_obj.k1 is None
    assert filter_obj.k2 is None


def test_gen_page_obj():
    page_data = {"limit": 1, "offset": 2}

    page_obj = utils.get_page_obj(page_data)

    assert page_obj.limit == 1
    assert page_obj.offset == 2

    page_data = {
        "limit": 1,
    }

    page_obj = utils.get_page_obj(page_data)

    assert page_obj.limit == 1
    assert page_obj.offset == 0

    # test slice property

    page_data = {"limit": 4, "offset": 0}

    page_obj = utils.get_page_obj(page_data)

    assert page_obj.slice_from == 0
    assert page_obj.slice_to == 4

    page_data = {"limit": 4, "offset": 3}

    page_obj = utils.get_page_obj(page_data)

    assert page_obj.slice_from == 3
    assert page_obj.slice_to == 7

    page_data = {"limit": 0, "offset": 0}

    page_obj = utils.get_page_obj(page_data)

    assert page_obj.slice_from == 0
    assert page_obj.slice_to is None
