"""
execution module for Nexus 3 security roles

:version: v0.4.0
:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions.

    Example:
      nexus3:
        hostname: '127.0.0.1:8081'
        username: 'admin'
        password: 'admin123'

"""

import json
import logging

from saltext.nexus3.utils import nexus3

log = logging.getLogger(__name__)

__outputter__ = {
    "sls": "highstate",
    "apply_": "highstate",
    "highstate": "highstate",
}

ROLES_PATH = "v1/security/roles"


def create(name, description="", privileges=None, roles=None):
    """
    name (str):
        name of role

    description (str):
        description of role

    privileges (list):
        list of privileges (Default: None)

    roles (list):
        roles to inherit from (Default: None)

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_roles.create name=test_role description='test role' roles="['nx-admin']"
    """

    if privileges is None:
        privileges = []
    if roles is None:
        roles = []

    ret = {
        "role": {},
    }

    path = ROLES_PATH

    payload = {
        "id": name,
        "name": name,
        "description": description,
        "privileges": privileges,
        "roles": roles,
    }

    nc = nexus3.NexusClient()

    resp = nc.post(path, payload)

    if resp["status"] == 200:
        ret["role"] = json.loads(resp["body"])
    else:
        ret["comment"] = f"could not create role {name}."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def delete(name):
    """
    name (str):
        name of role

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_roles.delete nx-admin
    """
    ret = {}

    path = ROLES_PATH + "/" + name
    nc = nexus3.NexusClient()

    resp = nc.delete(path)

    if resp["status"] == 204:
        ret["comment"] = f"role {name} deleted"
    else:
        ret["comment"] = f"could not delete role {name}."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def describe(name):
    """
    name (str):
        name of role

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_roles.describe nx-admin
    """

    ret = {
        "role": {},
    }

    path = ROLES_PATH + "/" + name
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp["status"] == 200:
        ret["role"] = json.loads(resp["body"])
    else:
        ret["comment"] = f"could not retrieve role {name}."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def list_all():
    """

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_roles.list_all
    """

    ret = {
        "roles": {},
    }

    path = ROLES_PATH
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp["status"] == 200:
        ret["roles"] = json.loads(resp["body"])
    else:
        ret["comment"] = "could not retrieve roles."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def update(name, description=None, privileges=None, roles=None):
    """
    name (str):
        name of role

    description (str):
        description of role (Default: None)

    privileges (list):
        list of privileges (Default: None)

    roles (list):
        roles to inherit from (Default: None)

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_roles.update name=test_role roles="['nx-admin']"
    """

    ret = {
        "role": {},
    }

    meta = describe(name)["role"]

    path = ROLES_PATH + "/" + name

    if description is not None:
        meta["description"] = description

    if privileges is not None:
        meta["privileges"] = privileges

    if roles is not None:
        meta["roles"] = roles

    nc = nexus3.NexusClient()
    resp = nc.put(path, meta)

    if resp["status"] == 204:
        ret["role"] = describe(name)["role"]
    else:
        ret["comment"] = f"could not update role {name}."
        ret["error"] = {
            "code": resp["status"],
            "msg": resp["body"],
        }

    return ret
