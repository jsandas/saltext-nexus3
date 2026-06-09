import json

from saltext.nexus3.modules import nexus3_roles


class _Client:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def get(self, path):
        self.calls.append(("get", path, None))
        return self._responses[("get", path)]

    def post(self, path, data):
        self.calls.append(("post", path, data))
        return self._responses[("post", path)]

    def put(self, path, data):
        self.calls.append(("put", path, data))
        return self._responses[("put", path)]

    def delete(self, path):
        self.calls.append(("delete", path, None))
        return self._responses[("delete", path)]


def test_create_sends_expected_payload(monkeypatch):
    responses = {
        ("post", "v1/security/roles"): {
            "status": 200,
            "body": json.dumps({"name": "testing-role", "roles": ["nx-admin"]}),
        }
    }
    client = _Client(responses)
    monkeypatch.setattr(
        nexus3_roles.nexus3,
        "NexusClient",
        lambda: client,
    )

    ret = nexus3_roles.create("testing-role", roles=["nx-admin"])

    assert ret["role"]["name"] == "testing-role"
    assert client.calls[0][0] == "post"
    assert client.calls[0][1] == "v1/security/roles"
    assert client.calls[0][2]["id"] == "testing-role"


def test_delete_success(monkeypatch):
    responses = {("delete", "v1/security/roles/testing-role"): {"status": 204, "body": ""}}
    client = _Client(responses)
    monkeypatch.setattr(nexus3_roles.nexus3, "NexusClient", lambda: client)

    ret = nexus3_roles.delete("testing-role")

    assert "deleted" in ret["comment"]


def test_update_merges_and_puts(monkeypatch):
    responses = {
        ("get", "v1/security/roles/testing-role"): {
            "status": 200,
            "body": json.dumps(
                {
                    "id": "testing-role",
                    "name": "testing-role",
                    "description": "old",
                    "privileges": ["nx-healthcheck-read"],
                    "roles": ["nx-anonymous"],
                }
            ),
        },
        ("put", "v1/security/roles/testing-role"): {"status": 204, "body": ""},
    }
    client = _Client(responses)
    monkeypatch.setattr(nexus3_roles.nexus3, "NexusClient", lambda: client)

    ret = nexus3_roles.update("testing-role", roles=["nx-admin"])

    assert ret["role"]["name"] == "testing-role"
    put_call = [call for call in client.calls if call[0] == "put"][0]
    assert put_call[2]["roles"] == ["nx-admin"]
