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
