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
    return {
        "nexus3": {
            "hostname": "http://127.0.0.1:8081",
            "username": "admin",
            "password": "admin123",
        }
    }


@pytest.fixture(scope="package", autouse=True)
def nexus_ready():  # pragma: no cover
    status_endpoint = "http://127.0.0.1:8081/service/rest/v1/status"
    for _ in range(30):
        try:
            with urlopen(status_endpoint, timeout=2) as ret:  # nosec B310
                if ret.status in (200, 401, 403):
                    return
        except URLError:
            pass
        except TimeoutError:
            pass
    pytest.skip("Nexus3 service is not reachable on http://127.0.0.1:8081")
