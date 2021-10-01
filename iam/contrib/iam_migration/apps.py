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

import os
import sys

import six
from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from iam.contrib.iam_migration.constants import APP_NAME, APP_VERBOSE_NAME, BK_IAM_MIGRATION_APP_NAME


class IAMMigrationConfig(AppConfig):
    name = APP_NAME
    label = name.rpartition(".")[2]
    default = True
    verbose_name = APP_VERBOSE_NAME

    def ready(self):
        # dist-packages: Debian distributions modify upstream Python
        for site_or_dist in ("site-packages", "dist-packages"):
            module_package_path = os.path.join("lib", "python%d.%d" % sys.version_info[:2], site_or_dist, "iam")
            if module_package_path in self.path:
                break
        else:
            return
        # Checking must be set `BK_IAM_MIGRATION_APP_NAME` for pip installation
        if not getattr(settings, BK_IAM_MIGRATION_APP_NAME, None):
            raise ImproperlyConfigured(
                "The %r setting must not be empty for iam with pip installation package" % BK_IAM_MIGRATION_APP_NAME
            )
        if not isinstance(settings.BK_IAM_MIGRATION_APP_NAME, six.string_types):
            raise ImproperlyConfigured(
                "The %r setting must be instance of %s" % (BK_IAM_MIGRATION_APP_NAME, six.string_types)
            )
        if settings.BK_IAM_MIGRATION_APP_NAME not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("The %r setting not in installed apps" % BK_IAM_MIGRATION_APP_NAME)
