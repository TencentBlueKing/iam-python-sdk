# -*- coding: utf-8 -*-


from django.conf import settings

from iam.contrib.iam_migration.constants import APP_NAME

MIGRATION_APP_NAME = getattr(settings, "BK_IAM_MIGRATION_APP_NAME", APP_NAME)
