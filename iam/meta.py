# -*- coding: utf-8 -*-


_SYSTEM = "system"
_RESOURCES = "resources"
_ACTIONS = "actions"

__meta_info__ = {_SYSTEM: {}, _RESOURCES: {}, _ACTIONS: {}}


def setup_system(system_id, system_name):
    __meta_info__[_SYSTEM].setdefault(system_id, {})["name"] = system_name


def get_system_name(system_id):
    return __meta_info__[_SYSTEM].get(system_id, {}).get("name")


def setup_resource(system_id, resource_id, resource_name):
    __meta_info__[_RESOURCES].setdefault(system_id, {}).setdefault(resource_id, {})["name"] = resource_name


def get_resource_name(system_id, resource_id):
    return __meta_info__[_RESOURCES].get(system_id, {}).get(resource_id, {}).get("name")


def setup_action(system_id, action_id, action_name):
    __meta_info__[_ACTIONS].setdefault(system_id, {}).setdefault(action_id, {})["name"] = action_name


def get_action_name(system_id, action_id):
    return __meta_info__[_ACTIONS].get(system_id, {}).get(action_id, {}).get("name")
