# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云-权限中心Python SDK(iam-python-sdk) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import abc

import six

from .constants import OP


@six.add_metaclass(abc.ABCMeta)
class Operator(object):
    def __init__(self, op):
        self.op = op

    @abc.abstractmethod
    def expr(self):
        pass

    def __repr__(self):
        return "operator:{}".format(self.op)


@six.add_metaclass(abc.ABCMeta)
class LogicalOperator(Operator):
    def __init__(self, op, content):
        super(LogicalOperator, self).__init__(op)

        # TODO: valid the content, should be list
        self.content = content

    def expr(self):
        separator = " %s " % self.op
        return "(%s)" % separator.join([c.expr() for c in self.content])

    def render(self, obj_set):
        separator = " %s " % self.op
        return "(%s)" % separator.join([c.render(obj_set) for c in self.content])

    @abc.abstractmethod
    def eval(self, obj_set):
        pass

    # TODO: expr with values, should change
    # @abc.abstractmethod
    # def expr_translate()


class AndOperator(LogicalOperator):
    def __init__(self, content):
        super(AndOperator, self).__init__(OP.AND, content)

    def eval(self, obj_set):
        # return all([c.eval(obj_set) for c in self.content])
        # Short-circuit evaluation
        for c in self.content:
            if not c.eval(obj_set):
                return False
        return True


class OrOperator(LogicalOperator):
    def __init__(self, content):
        super(OrOperator, self).__init__(OP.OR, content)

    def eval(self, obj_set):
        # return any([c.eval(obj_set) for c in self.content])
        # Short-circuit evaluation
        for c in self.content:
            if c.eval(obj_set):
                return True
        return False


@six.add_metaclass(abc.ABCMeta)
class BinaryOperator(Operator):
    def __init__(self, op, field, value):
        super(BinaryOperator, self).__init__(op)
        self.field = field
        self.value = value

    def render(self, obj_set):
        value = self.value
        if isinstance(self.value, six.string_types):
            value = "'%s'" % self.value

        attr = obj_set.get(self.field)
        if isinstance(attr, six.string_types):
            attr = "'%s'" % attr

        return "(%s %s %s)" % (attr, self.op, value)

    def expr(self):
        value = self.value
        if isinstance(self.value, six.string_types):
            value = "'%s'" % self.value

        return "(%s %s %s)" % (self.field, self.op, value)

    @abc.abstractmethod
    def calculate(self, left, right):
        pass

    def _eval_positive(self, object_attr, is_object_attr_array, policy_value):  # NOQA
        """
        positive:
        - 1   hit: return True
        - all miss: return False

        e.g.
        op = eq => one of attr equals one of value

        attr = 1; value = 1; True
        attr = [1, 2]; value = 2; True
        """
        # if self.op == OP.ANY:
        #     return self.calculate(object_attr, policy_value)

        # NOTE: here, the policyValue should not be array!
        # It's single value (except: the NotIn op policyValue is an array)
        if is_object_attr_array:
            for a in object_attr:
                if self.calculate(a, policy_value):
                    return True
            return False

        return self.calculate(object_attr, policy_value)

    def _eval_negative(self, object_attr, is_object_attr_array, policy_value):  # NOQA
        """
        negative:
        - 1   miss: return False
        - all hit: return True

        e.g.
        op = not_eq => all of attr should not_eq to all of the value

        attr = 1; value = 2; True
        attr = [1, 2]; value = 3; True
        """

        # NOTE: here, the policyValue should not be array!
        # It's single value (except: the NotIn op policyValue is an array)
        if is_object_attr_array:
            for a in object_attr:
                if not self.calculate(a, policy_value):
                    return False
            return True

        return self.calculate(object_attr, policy_value)

    def eval(self, obj_set):
        """
        type: str/numberic/boolean
        the value support `type` or `[type]`
        the obj_set.get(self.field) support `type` or `[type]`

        if one of them is array, or both array
        calculate each item in array
        """
        object_attr = obj_set.get(self.field)
        policy_value = self.value

        is_object_attr_array = isinstance(object_attr, (list, tuple))
        is_policy_value_array = isinstance(policy_value, (list, tuple))

        # any
        if self.op == OP.ANY:
            return True

        # if you add new operator, please read this first: https://github.com/TencentBlueKing/bk-iam-saas/issues/1293
        # valid the attr and value first
        if self.op in (OP.IN, OP.NOT_IN):
            # a in b, a not_in b
            # b should be an array, while a can be a single or an array
            # so we should make the in expression b always be an array
            if not is_policy_value_array:
                return False

            if self.op == OP.IN:
                return self._eval_positive(object_attr, is_object_attr_array, policy_value)
            else:
                return self._eval_negative(object_attr, is_object_attr_array, policy_value)

        if self.op in (OP.CONTAINS, OP.NOT_CONTAINS):
            # a contains b,  a not_contains b
            # a should be an array, b should be a single value
            # so, we should make the contains expression b always be a single string,
            # while a can be a single value or an array
            if not is_object_attr_array or is_policy_value_array:
                return False
            return self.calculate(object_attr, policy_value)

        if self.op in (
            OP.EQ,
            OP.NOT_EQ,
            OP.LT,
            OP.LTE,
            OP.GT,
            OP.GTE,
            OP.STARTS_WITH,
            OP.NOT_STARTS_WITH,
            OP.ENDS_WITH,
            OP.NOT_ENDS_WITH,
            OP.STRING_CONTAINS,
        ):
            # a starts_with b, a not_starts_with, a ends_with b, a not_ends_with b
            # b should be a single value, while a can be a single value or an array
            if is_policy_value_array:
                return False

            # positive and negative operator
            # ==  命中一个即返回
            # !=  需要全部遍历完, 确认全部不等于才返回?
            if self.op.startswith("not_"):
                return self._eval_negative(object_attr, is_object_attr_array, policy_value)
            else:
                return self._eval_positive(object_attr, is_object_attr_array, policy_value)


class EqualOperator(BinaryOperator):
    def __init__(self, field, value):
        super(EqualOperator, self).__init__(OP.EQ, field, value)

    def calculate(self, left, right):
        return left == right


class NotEqualOperator(BinaryOperator):
    def __init__(self, field, value):
        super(NotEqualOperator, self).__init__(OP.NOT_EQ, field, value)

    def calculate(self, left, right):
        return left != right


class InOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be list or string(sequence?)
        super(InOperator, self).__init__(OP.IN, field, value)

    def calculate(self, left, right):
        return left in right


class NotInOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be list or string(sequence?)
        super(NotInOperator, self).__init__(OP.NOT_IN, field, value)

    def calculate(self, left, right):
        return left not in right


class ContainsOperator(BinaryOperator):
    def __init__(self, field, value):
        super(ContainsOperator, self).__init__(OP.CONTAINS, field, value)

    def calculate(self, left, right):
        return right in left


class NotContainsOperator(BinaryOperator):
    def __init__(self, field, value):
        super(NotContainsOperator, self).__init__(OP.NOT_CONTAINS, field, value)

    def calculate(self, left, right):
        return right not in left


class StartsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        super(StartsWithOperator, self).__init__(OP.STARTS_WITH, field, value)

    def calculate(self, left, right):
        return left.startswith(right)


class NotStartsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        super(NotStartsWithOperator, self).__init__(OP.NOT_STARTS_WITH, field, value)

    def calculate(self, left, right):
        return not left.startswith(right)


class EndsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        super(EndsWithOperator, self).__init__(OP.ENDS_WITH, field, value)

    def calculate(self, left, right):
        return left.endswith(right)


class NotEndsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        super(NotEndsWithOperator, self).__init__(OP.NOT_ENDS_WITH, field, value)

    def calculate(self, left, right):
        return not left.endswith(right)


class StringContainsOperator(BinaryOperator):
    def __init__(self, field, value):
        super(StringContainsOperator, self).__init__(OP.STRING_CONTAINS, field, value)

    def calculate(self, left, right):
        return right in left


class LTOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(LTOperator, self).__init__(OP.LT, field, value)

    def calculate(self, left, right):
        return left < right


class LTEOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(LTEOperator, self).__init__(OP.LTE, field, value)

    def calculate(self, left, right):
        return left <= right


class GTOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(GTOperator, self).__init__(OP.GT, field, value)

    def calculate(self, left, right):
        return left > right


class GTEOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(GTEOperator, self).__init__(OP.GTE, field, value)

    def calculate(self, left, right):
        return left >= right


class AnyOperator(BinaryOperator):
    def __init__(self, field, value):
        super(AnyOperator, self).__init__(OP.ANY, field, value)

    def calculate(self, left, right):
        return True


BINARY_OPERATORS = {
    OP.EQ: EqualOperator,
    OP.NOT_EQ: NotEqualOperator,
    OP.IN: InOperator,
    OP.NOT_IN: NotInOperator,
    OP.CONTAINS: ContainsOperator,
    OP.NOT_CONTAINS: NotContainsOperator,
    OP.STARTS_WITH: StartsWithOperator,
    OP.NOT_STARTS_WITH: NotStartsWithOperator,
    OP.ENDS_WITH: EndsWithOperator,
    OP.NOT_ENDS_WITH: NotEndsWithOperator,
    OP.STRING_CONTAINS: StringContainsOperator,
    OP.LT: LTOperator,
    OP.LTE: LTEOperator,
    OP.GT: GTOperator,
    OP.GTE: GTEOperator,
    OP.ANY: AnyOperator,
}
