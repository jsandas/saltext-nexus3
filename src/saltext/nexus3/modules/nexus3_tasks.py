"""
execution module for Nexus 3 tasks

:version: v0.4.0
:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions.

    nexus3: hostname: '127.0.0.1:8081' username: 'admin' password: 'admin123'

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

TASKS_PATH = "v1/tasks"


def describe(task_id):
    """
    task_id (str):
        task id

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_tasks.describe task_id=512be2c3-aa04-448f-b0ce-2047eee34903
    """

    ret = {
        "task": {},
    }

    path = TASKS_PATH + "/" + task_id

    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp["status"] == 200:
        ret["task"] = json.loads(resp["body"])
    else:
        ret["comment"] = f"could not get task: {task_id}"
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def list_all():
    """

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_tasks.list_all

    TODO:
        add support for the continuationToken for larger lists
    """

    ret = {
        "tasks": {},
    }

    path = TASKS_PATH

    nc = nexus3.NexusClient()

    resp = nc.get(path)

    if resp["status"] == 200:
        ret["tasks"] = json.loads(resp["body"])
    else:
        ret["comment"] = "could not get tasks"
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def run(task_id):
    """
    task_id (str):
        task id

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_tasks.run task_id=512be2c3-aa04-448f-b0ce-2047eee34903
    """

    ret = {
        "task": {},
    }

    path = TASKS_PATH + "/" + task_id + "/run"

    nc = nexus3.NexusClient()

    resp = nc.post(path, None)

    if resp["status"] == 204:
        ret["task"] = f"ran task: {task_id}"
    else:
        ret["comment"] = f"could not run task: {task_id}"
        if resp["status"] == 404:
            msg = "task not found"
        elif resp["status"] == 405:
            msg = "task is disabled"
        else:
            msg = resp["body"]

        ret["error"] = {"code": resp["status"], "msg": msg}

    return ret


def stop(task_id):
    """
    task_id (str):
        task id

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_tasks.stop task_id=512be2c3-aa04-448f-b0ce-2047eee34903
    """

    ret = {
        "task": {},
    }

    path = TASKS_PATH + "/" + task_id + "/run"

    nc = nexus3.NexusClient()

    resp = nc.post(path, None)

    if resp["status"] == 204:
        ret["task"] = f"stopped task: {task_id}"
    else:
        ret["comment"] = f"could not stop task: {task_id}"
        if resp["status"] == 404:
            msg = "task not found"
        elif resp["status"] == 405:
            msg = "task is disabled"
        else:
            msg = resp["body"]

        ret["error"] = {"code": resp["status"], "msg": msg}

    return ret
