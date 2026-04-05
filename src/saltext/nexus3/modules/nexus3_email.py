"""
execution module for Nexus 3 email settings

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

EMAIL_PATH = "v1/email"


def configure(  # pylint: disable=invalid-name
    enabled,
    from_address="nexus@example.org",
    host="localhost",
    nexus_trust_store_enabled=False,
    password=None,
    port=0,
    ssl_on_connect_enabled=False,
    ssl_server_identity_check_enabled=False,
    start_tls_enabled=False,
    start_tls_required=False,
    subjectPrefix=None,
    username="",
):
    """
    enabled (bool):
        enable email support [True|False]

    from_address (str):
        mail from address (Default: nexus@example.org)

    host (string):
        smtp hostname (Default: localhost)

    nexus_trust_store_enabled (bool):
        use nexus truststore [True|False] (Default: False)
        .. note::
            Ensure CA certificate is add to the Nexus trustore

    password (str):
        smtp password (Default: None)

    port (int):
        smtp port (Default: 0)

    ssl_on_connect_enabled (bool):
        connect using tls (SMTPS) (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    ssl_server_identity_check_enabled (bool):
        verify server certificate (Default: False)

    start_tls_enabled (bool):
        enable starttls (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    start_tls_required (bool):
        require starttls (Default: False)
        .. note::
            tls_connect and starttls should be mutually exclusive

    subjectPrefix (str):
        prefix for subject in emails (Default: None)

    username (str):
        smtp username (Default: '')

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.configure enabled=True host=smtp.example.com

        salt myminion nexus3_email.configure enabled=False
    """

    ret = {"email": {}}

    payload = {
        "enabled": enabled,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "from_address": from_address,
        "subjectPrefix": subjectPrefix,
        "start_tls_enabled": start_tls_enabled,
        "start_tls_required": start_tls_required,
        "ssl_on_connect_enabled": ssl_on_connect_enabled,
        "ssl_server_identity_check_enabled": ssl_server_identity_check_enabled,
        "nexus_trust_store_enabled": nexus_trust_store_enabled,
    }

    nc = nexus3.NexusClient()
    resp = nc.put(EMAIL_PATH, payload)

    if resp["status"] != 204:
        ret["comment"] = "could not to configure emails settings."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}
        return ret

    email_config = describe()
    ret["email"] = email_config["email"]

    return ret


def describe():
    """

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.describe
    """

    ret = {"email": {}}

    nc = nexus3.NexusClient()
    resp = nc.get(EMAIL_PATH)

    if resp["status"] == 200:
        ret["email"] = json.loads(resp["body"])
    else:
        ret["comment"] = "could not to retrieve email settings"
        ret["error"] = "code:{} msg:{}".format(resp["status"], resp["body"])

    return ret


def reset():
    """

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.reset
    """

    ret = {}

    nc = nexus3.NexusClient()
    resp = nc.delete(EMAIL_PATH)

    if resp["status"] == 204:
        ret["comment"] = "email settings reset"
    else:
        ret["comment"] = "could not reset email settings"
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret


def verify(to):
    """
    to (str):
        address to send test email to

    CLI Example:

    .. code-block:: bash

        salt myminion nexus3_email.verify
    """
    ret = {}

    verify_path = EMAIL_PATH + "/verify"

    nc = nexus3.NexusClient()
    resp = nc.post(verify_path, to)

    if resp["status"] == 200:
        status = json.loads(resp["body"])
        if status["success"]:
            ret["comment"] = f"email sent to {to}."
        else:
            ret["comment"] = "could not send email."
            ret["error"] = status["reason"]
    else:
        ret["comment"] = "could not send email."
        ret["error"] = {"code": resp["status"], "msg": resp["body"]}

    return ret
