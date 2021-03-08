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

from iam import Converter

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class BaseConverterTest(unittest.TestCase):
    """
    for abstractmethod, make sure no absent
    """

    @patch.object(Converter, "__abstractmethods__", set())
    def test(self):
        self.instance = Converter()

        self.instance._eq(1, 1)
        self.instance._not_eq(1, 1)
        self.instance._in(1, 1)
        self.instance._not_in(1, 1)
        self.instance._contains(1, 1)
        self.instance._not_contains(1, 1)
        self.instance._starts_with(1, 1)
        self.instance._not_starts_with(1, 1)
        self.instance._ends_with(1, 1)
        self.instance._not_ends_with(1, 1)

        self.instance._lt(1, 1)
        self.instance._lte(1, 1)
        self.instance._gt(1, 1)
        self.instance._gte(1, 1)

        self.instance._any(1, 1)

        self.instance._and(1)
        self.instance._or(1)

        self.instance.convert(None)
