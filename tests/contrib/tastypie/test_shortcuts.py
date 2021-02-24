# -*- coding: utf-8 -*-
# import pytest
# import unittest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

import sys

sys.modules["tastypie.exceptions"] = MagicMock()

from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response_for_resources_list
from iam.exceptions import MultiAuthFailedException


class Resource:
    def __init__(self, rid):
        self.id = rid


def test_allow_or_raise_immediate_response_for_resources_list__allowed():
    system = "system"
    subject = "subject"
    action = "action"
    resources = [[Resource("r1")], [Resource("r2")]]

    iam = MagicMock()
    iam.batch_is_allowed = MagicMock(return_value={"r1": True, "r2": True})

    Request = MagicMock()

    with patch("iam.contrib.tastypie.shortcuts.Request", Request):
        allow_or_raise_immediate_response_for_resources_list(iam, system, subject, action, resources)

    Request.assert_called_once_with(system, subject, action, [], None)


def test_allow_or_raise_immediate_response_for_resources_list__raise():
    system = "system"
    subject = "subject"
    action = "action"
    resources = [[Resource("r1")], [Resource("r2")]]

    iam = MagicMock()
    iam.batch_is_allowed = MagicMock(return_value={"r1": True, "r2": False})
    not_allowed_resources_list = [resources[1]]

    Request = MagicMock()

    with patch("iam.contrib.tastypie.shortcuts.Request", Request):
        try:
            allow_or_raise_immediate_response_for_resources_list(iam, system, subject, action, resources)
        except MultiAuthFailedException as e:
            assert e.system == system
            assert e.subject == subject
            assert e.action == action
            assert e.resources_list == not_allowed_resources_list
        else:
            assert False, "allow_or_raise_auth_failed did not raise"

    Request.assert_called_once_with(system, subject, action, [], None)
