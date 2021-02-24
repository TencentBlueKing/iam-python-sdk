# -*- coding: utf-8 -*-


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
