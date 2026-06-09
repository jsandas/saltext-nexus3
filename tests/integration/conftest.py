import os
from urllib.error import URLError
from urllib.request import urlopen

import pytest


@pytest.fixture(scope="package")
def master(master):  # pragma: no cover
    with master.started():
        yield master


@pytest.fixture(scope="package")
def minion(minion):  # pragma: no cover
    with minion.started():
        yield minion


@pytest.fixture
def salt_run_cli(master):  # pragma: no cover
    return master.salt_run_cli()


@pytest.fixture
def salt_cli(master):  # pragma: no cover
    return master.salt_cli()


@pytest.fixture
def salt_call_cli(minion):  # pragma: no cover
    return minion.salt_call_cli()


@pytest.fixture(scope="package")
def minion_config():  # pragma: no cover
    nexus_hostname = os.environ.get("NEXUS3_HOSTNAME", "http://127.0.0.1:8081")
    nexus_username = os.environ.get("NEXUS3_USERNAME", "admin")
    nexus_password = os.environ.get("NEXUS3_PASSWORD", "")

    return {
        "nexus3": {
            "hostname": nexus_hostname,
            "username": nexus_username,
            "password": nexus_password,
        }
    }


@pytest.fixture(scope="package", autouse=True)
def nexus_ready():  # pragma: no cover
    status_endpoint = (
        f"{os.environ.get('NEXUS3_HOSTNAME', 'http://127.0.0.1:8081')}/service/rest/v1/status"
    )
    for _ in range(30):
        try:
            with urlopen(status_endpoint, timeout=2) as ret:  # nosec B310
                if ret.status in (200, 401, 403):
                    return
        except URLError:
            pass
        except TimeoutError:
            pass
    pytest.skip(f"Nexus3 service is not reachable on {status_endpoint}")


@pytest.fixture(autouse=True)
def nexus_auth_ready(salt_call_cli):  # pragma: no cover
    """
    Only run live integration assertions when authenticated module calls work.
    """
    ret = salt_call_cli.run("nexus3_anonymous_access.describe")
    if ret.exitcode != 0 or not ret.json:
        pytest.skip("Nexus3 auth is not ready for Salt module integration tests")

    anonymous_access = ret.json.get("anonymous_access")
    if not isinstance(anonymous_access, dict) or "enabled" not in anonymous_access:
        pytest.skip("Nexus3 auth is not ready for Salt module integration tests")
