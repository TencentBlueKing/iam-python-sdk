# -*- coding: utf-8 -*-


from .__version__ import __version__  # noqa

from .eval.object import DictObject, ObjectSet  # noqa
from .eval.constants import OP  # noqa
from .eval.expression import make_expression  # noqa
from .eval.operators import (  # noqa
    AndOperator,
    OrOperator,
    EqualOperator,
    NotEqualOperator,
    InOperator,
    NotInOperator,
    ContainsOperator,
    NotContainsOperator,
    StartsWithOperator,
    NotStartsWithOperator,
    EndsWithOperator,
    NotEndsWithOperator,
    LTOperator,
    LTEOperator,
    GTOperator,
    GTEOperator,
    AnyOperator,
    Operator,
    LogicalOperator,
    BinaryOperator,
)

from .contrib.converter.base import Converter  # noqa
from .contrib.converter.sql import SQLConverter  # noqa
from .contrib.converter.queryset import DjangoQuerySetConverter, PathEqDjangoQuerySetConverter  # noqa

from .auth.models import Subject, Action, Resource  # noqa
from .auth.models import Request, MultiActionRequest  # noqa

from .iam import IAM  # noqa
from .dummy_iam import DummyIAM # noqa

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
