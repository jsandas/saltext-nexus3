def test_status_check_module(salt_call_cli):
    ret = salt_call_cli.run("nexus3_status.check")

    assert ret.exitcode == 0
    assert ret.json
    assert "status" in ret.json


def test_anonymous_access_module_describe(salt_call_cli):
    ret = salt_call_cli.run("nexus3_anonymous_access.describe")

    assert ret.exitcode == 0
    assert ret.json
    assert "anonymous_access" in ret.json
    assert "enabled" in ret.json["anonymous_access"]


def test_security_state_test_mode(salt_call_cli):
    ret = salt_call_cli.run(
        "state.single",
        "nexus3_security.anonymous_access",
        "name=anon-check",
        "enabled=False",
        "test=True",
    )

    assert ret.exitcode == 0
    assert ret.json
    state_ret = list(ret.json.values())[0]
    assert state_ret["result"] in (None, True)
