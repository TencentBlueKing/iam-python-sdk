# -*- coding: utf-8 -*-


from django.apps import AppConfig

from iam.contrib.iam_migration.constants import APP_NAME


class IAMMigrationConfig(AppConfig):
    name = APP_NAME
