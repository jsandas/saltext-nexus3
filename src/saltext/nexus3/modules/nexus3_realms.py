"""
execution module for Nexus 3 security realms

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

REALMS_PATH = "v1/security/realms"


def list_active():
    """

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.list_active
    """

    ret = {
        "realms": {},
    }

    path = REALMS_PATH + "/active"
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp["status"] == 200:
        ret["realms"] = json.loads(resp["body"])
    else:
        ret["comment"] = "could not retrieve active realms."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def list_all():
    """

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.list_all
    """

    ret = {
        "realms": {},
    }

    path = REALMS_PATH + "/available"
    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp["status"] == 200:
        ret["realms"] = json.loads(resp["body"])
    else:
        ret["comment"] = "could not retrieve available realms."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def reset():
    """
    Resets realms to default

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.reset
    """

    ret = {
        "realms": {},
    }

    path = REALMS_PATH + "/active"

    # these are the defaults enabled
    # upon first start of Nexus 3
    payload = ["NexusAuthenticatingRealm", "NexusAuthorizingRealm", "NpmToken"]

    nc = nexus3.NexusClient()

    resp = nc.put(path, payload)

    if resp["status"] == 204:
        ret["realms"] = list_active()["realms"]
        ret["comment"] = "realms reset to defaults."
    else:
        ret["comment"] = "could not reset realms."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def update(auth_realms=None):
    """
    auth_realms (list):
        list of realms in order they should be used
        .. note::
            Include all desired realms in list as this will override
            the current list

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_realms.update auth_realms="['NexusAuthenticatingRealm','NexusAuthorizingRealm','NpmToken','DockerToken']"
    """

    if auth_realms is None:
        auth_realms = []

    ret = {
        "realms": {},
    }

    path = REALMS_PATH + "/active"

    nc = nexus3.NexusClient()

    resp = nc.put(path, auth_realms)

    if resp["status"] == 204:
        ret["realms"] = list_active()["realms"]
        ret["comment"] = "realms updated."
    else:
        ret["comment"] = "could not update realms."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret
