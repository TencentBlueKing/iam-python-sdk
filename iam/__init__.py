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


# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

from .__version__ import __version__  # noqa
from .auth.models import Action, MultiActionRequest, Request, Resource, Subject  # noqa
from .contrib.converter.base import Converter  # noqa
from .contrib.converter.queryset import DjangoQuerySetConverter, PathEqDjangoQuerySetConverter  # noqa
from .contrib.converter.sql import SQLConverter  # noqa
from .dummy_iam import DummyIAM  # noqa
from .eval.constants import OP  # noqa
from .eval.expression import make_expression  # noqa
from .eval.object import DictObject, ObjectSet  # noqa
from .eval.operators import (  # noqa
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
    Operator,
    OrOperator,
    StartsWithOperator,
)
from .iam import IAM  # noqa

logging.getLogger(__name__).addHandler(NullHandler())
