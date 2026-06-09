"""
state module for Nexus 3 email settings

:version: v0.4.0
:configuration: In order to connect to Nexus 3, certain configuration is required
    in /etc/salt/minion on the relevant minions.

    nexus3: hostname: '127.0.0.1:8081' username: 'admin' password: 'admin123'

"""

import logging

log = logging.getLogger(__name__)


def clear(name):
    """
    name (str):
        state id name
        do not provide this argument, this is only here because salt passes this arg always

    .. code-block:: yaml

        clear_email:
          nexus3_email.clear

    """

    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "email configuration will be reset to defaults"
        return ret

    reset_results = __salt__["nexus3_email.reset"]()

    if "error" in reset_results.keys():
        ret["result"] = False
        ret["comment"] = reset_results["error"]
        return ret

    ret["changes"] = reset_results

    return ret


def configure(  # pylint: disable=invalid-name
    name,
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
    name (str):
        state id name
        do not provide this argument, this is only here because salt passes this arg always

    enabled (bool):
        enable email support [True|False]

    from_address (str):
        mail from address (Default: nexus@example.org)

    host (string):
        smtp hostname (Default: localhost)

    nexus_trust_store_enabled (bool):
        use nexus truststore [True|False] (Default: False)
        Ensure CA certificate is add to the Nexus trustore

    password (str):
        smtp password (Default: None)

    port (int):
        smtp port (Default: 0)

    ssl_on_connect_enabled (bool):
        connect using tls (SMTPS) (Default: False)
        ssl_on_connect_enabled and start_tls_enabled/start_tls_required should be mutually exclusive

    ssl_server_identity_check_enabled (bool):
        verify server certificate (Default: False)

    start_tls_enabled (bool):
        enable starttls (Default: False)
        ssl_on_connect_enabled and start_tls_enabled/start_tls_required should be mutually exclusive

    start_tls_required (bool):
        require starttls (Default: False)
        ssl_on_connect_enabled and start_tls_enabled/start_tls_required should be mutually exclusive


    subjectPrefix (str):
        prefix for subject in emails (Default: None)

    username (str):
        smtp username (Default: '')

    .. code-block:: yaml

        setup_email:
          nexus3_email.configure:
            - enabled: True
            - host: smtp@example.com
            - port: 587
            - from_address: test@example.com
            - start_tls_enabled: True
    """

    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    ret["comment"] = "email configuration is in desired state."
    is_update = False
    meta = __salt__["nexus3_email.describe"]()
    updates = {}

    if "error" in meta.keys():
        ret["result"] = False
        ret["comment"] = meta["error"]
        return ret

    input_vars = locals()
    for k, v in meta["email"].items():
        if v != input_vars[k]:
            is_update = True
            updates[k] = input_vars[k]

    if is_update:
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"email configuration will be updated with: {updates}"
            return ret

        configure_results = __salt__["nexus3_email.configure"](
            enabled,
            from_address,
            host,
            nexus_trust_store_enabled,
            password,
            port,
            ssl_on_connect_enabled,
            ssl_server_identity_check_enabled,
            start_tls_enabled,
            start_tls_required,
            subjectPrefix,
            username,
        )

        if "error" in configure_results.keys():
            ret["result"] = False
            ret["comment"] = configure_results["error"]
            return ret

        ret["changes"] = configure_results

    return ret
