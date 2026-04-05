#!/usr/bin/env python3

import salt.client

client = salt.client.LocalClient()


def test_cleanup():
    # clean the slate
    client.cmd("test.minion", "nexus3_email.reset")


def test_configure_email():
    ret = client.cmd(
        "test.minion",
        "nexus3_email.configure",
        [
            "enabled=True",
            "host=notlocalhost",
            "port=587",
            "from_address=test@example.com",
            "start_tls_enabled=True",
        ],
    )

    # print(ret)
    assert ret["test.minion"]["email"]["host"] == "notlocalhost", "host incorrect"

    assert ret["test.minion"]["email"]["port"] == 587, "port incorrect"

    assert ret["test.minion"]["email"]["from_address"] == "test@example.com", "from_address incorrect"

    assert ret["test.minion"]["email"]["start_tls_enabled"] == True, "start_tls_enabled incorrect"


def test_describe_email():
    client.cmd(
        "test.minion",
        "nexus3_email.configure",
        [
            "enabled=True",
            "host=notlocalhost",
            "port=465",
            "from_address=test@example.com",
            "ssl_on_connect_enabled=True",
        ],
    )

    ret = client.cmd("test.minion", "nexus3_email.describe")

    # print(ret)
    assert ret["test.minion"]["email"]["host"] == "notlocalhost", "host incorrect"

    assert ret["test.minion"]["email"]["port"] == 465, "port incorrect"

    assert ret["test.minion"]["email"]["from_address"] == "test@example.com", "from_address incorrect"

    assert (
        ret["test.minion"]["email"]["ssl_on_connect_enabled"] == True
    ), "ssl_on_connect_enabled incorrect"
