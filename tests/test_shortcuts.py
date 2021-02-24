# -*- coding: utf-8 -*-
# import pytest
# import unittest

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import patch, MagicMock

from iam.exceptions import AuthFailedException
from iam.shortcuts import allow_or_raise_auth_failed


def test_allow_or_raise_auth_failed__allowed():
    system = "system"
    subject = "subject"
    action = "action"
    resources = ["r1", "r2"]

    iam = MagicMock()
    iam.is_allowed = MagicMock(return_value=True)

    Request = MagicMock()

    with patch("iam.shortcuts.Request", Request):
        allow_or_raise_auth_failed(iam, system, subject, action, resources)

    Request.assert_called_once_with(system, subject, action, resources, None)


def test_allow_or_raise_auth_failed__raise():
    system = "system"
    subject = "subject"
    action = "action"
    resources = ["r1", "r2"]

    iam = MagicMock()
    iam.is_allowed = MagicMock(return_value=False)

    Request = MagicMock()

    with patch("iam.shortcuts.Request", Request):
        try:
            allow_or_raise_auth_failed(iam, system, subject, action, resources)
        except AuthFailedException as e:
            assert e.system == system
            assert e.subject == subject
            assert e.action == action
            assert e.resources == resources
        else:
            assert False, "allow_or_raise_auth_failed did not raise"

    Request.assert_called_once_with(system, subject, action, resources, None)
