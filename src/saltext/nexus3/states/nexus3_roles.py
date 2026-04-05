"""
state module for Nexus 3 roles

:version: v0.4.0
:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions.

    Example:
      nexus3:
        hostname: '127.0.0.1:8081'
        username: 'admin'
        password: 'admin123'

"""

import logging

log = logging.getLogger(__name__)


def absent(name):
    """
    name (str):
        name of role

    .. code-block:: yaml

        testing1:
          nexus3_roles.absent
    """

    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    exists = True

    meta = __salt__["nexus3_roles.describe"](name)

    if not meta["role"]:
        exists = False

    if exists:
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"role {name} will be deleted."
            return ret

        resp = __salt__["nexus3_roles.delete"](name)
        if "error" in resp.keys():
            ret["result"] = False
            ret["comment"] = resp["error"]
        else:
            ret["changes"] = resp
    else:
        ret["comment"] = f"role {name} does not exist"

    return ret


def present(name, description, privileges, roles):
    """
    name (str):
        name of role

    description (str):
        description of role

    privileges (list):
        list of privileges
        .. note::
            requires at least an empty list

    roles (list):
        roles to inherit from
        .. note::
            requires at least an empty list

    .. code-block:: yaml

        create_role:
          nexus3_roles.present:
            - name: test_role
            - description: 'test role'
            - roles: ['nx-admin']
    """

    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    exists = True
    # get value of realms
    meta = __salt__["nexus3_roles.describe"](name)

    if meta["role"] == {}:
        exists = False

    if not exists:
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"role {name} will be created."
            return ret

        create_results = __salt__["nexus3_roles.create"](name, description, privileges, roles)

        if "error" in create_results.keys():
            ret["result"] = False
            ret["comment"] = create_results["error"]
            return ret

        ret["changes"] = create_results

    if exists:
        is_update = False
        updates = {}

        if meta["role"]["description"] != description:
            updates["description"] = description
            is_update = True

        if meta["role"]["privileges"] != privileges:
            updates["privileges"] = privileges
            is_update = True

        if meta["role"]["roles"] != roles:
            updates["roles"] = roles
            is_update = True

        if __opts__["test"]:

            if is_update:
                ret["result"] = None
                ret["comment"] = f"role {name} will be updated with: {updates}"
                return ret
            else:
                ret["comment"] = f"role {name} is in desired state."

                return ret

        if not is_update:
            ret["comment"] = f"role {name} is in desired state."
            return ret

        update_results = __salt__["nexus3_roles.update"](name, description, privileges, roles)

        if "error" in update_results.keys():
            ret["result"] = False
            ret["comment"] = update_results["error"]
            return ret

        ret["changes"] = updates

    return ret
