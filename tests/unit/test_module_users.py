import json

from saltext.nexus3.modules import nexus3_users


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


def test_create_uses_default_role(monkeypatch):
    responses = {
        ("post", "v1/security/users"): {
            "status": 200,
            "body": json.dumps({"userId": "user-a", "roles": ["nx-anonymous"]}),
        }
    }
    client = _Client(responses)
    monkeypatch.setattr(nexus3_users.nexus3, "NexusClient", lambda: client)

    ret = nexus3_users.create(
        "user-a",
        "secret",
        "user-a@example.com",
        "User",
        "A",
    )

    assert ret["user"]["userId"] == "user-a"
    assert client.calls[0][2]["roles"] == ["nx-anonymous"]


def test_describe_finds_matching_user(monkeypatch):
    responses = {
        ("get", "v1/security/users"): {
            "status": 200,
            "body": json.dumps(
                [
                    {"userId": "other"},
                    {"userId": "target", "firstName": "Target"},
                ]
            ),
        }
    }
    client = _Client(responses)
    monkeypatch.setattr(nexus3_users.nexus3, "NexusClient", lambda: client)

    ret = nexus3_users.describe("target")

    assert ret["user"]["userId"] == "target"


def test_update_password_happy_path(monkeypatch):
    responses = {
        ("get", "v1/security/users"): {
            "status": 200,
            "body": json.dumps([{"userId": "target", "roles": ["nx-admin"]}]),
        },
        ("put", "v1/security/users/target/change-password"): {"status": 204, "body": ""},
    }
    client = _Client(responses)
    monkeypatch.setattr(nexus3_users.nexus3, "NexusClient", lambda: client)

    ret = nexus3_users.update_password("target", "new-password")

    assert "updated password" in ret["comment"]
    put_call = [call for call in client.calls if call[0] == "put"][0]
    assert put_call[2] == "new-password"
