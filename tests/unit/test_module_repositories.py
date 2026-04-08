import json

from saltext.nexus3.modules import nexus3_repositories


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


def test_format_url_string_maven2_maps_to_maven():
    assert nexus3_repositories._format_url_string("maven2") == "maven"
    assert nexus3_repositories._format_url_string("docker") == "docker"


def test_delete_handles_not_present(monkeypatch):
    client = _Client({("delete", "v1/repositories/repo-a"): {"status": 404, "body": ""}})
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)

    ret = nexus3_repositories.delete("repo-a")

    assert "not present" in ret["comment"]


def test_describe_returns_matching_repository(monkeypatch):
    payload = [
        {"name": "other", "type": "proxy"},
        {"name": "repo-a", "type": "hosted"},
    ]
    client = _Client(
        {("get", "v1/repositorySettings"): {"status": 200, "body": json.dumps(payload)}}
    )
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)

    ret = nexus3_repositories.describe("repo-a")

    assert ret["repository"]["name"] == "repo-a"
    assert ret["repository"]["type"] == "hosted"


def test_list_all_returns_error_on_non_200(monkeypatch):
    client = _Client({("get", "v1/repositorySettings"): {"status": 500, "body": "boom"}})
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)

    ret = nexus3_repositories.list_all()

    assert "Error retrieving repositories" in ret["comment"]
    assert ret["error"]["code"] == 500


def test_group_rejects_empty_group_members(monkeypatch):
    monkeypatch.setattr(
        nexus3_repositories,
        "describe",
        lambda _name: {"repository": {}},
    )

    ret = nexus3_repositories.group(
        name="group-a",
        repository_format="docker",
        group_members=[],
    )

    assert "could not create repository" in ret["comment"]
    assert ret["error"] == "group_members cannot be empty"


def test_proxy_docker_create_uses_expected_path_and_payload(monkeypatch):
    client = _Client({("post", "v1/repositories/docker/proxy"): {"status": 201, "body": ""}})
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)

    describe_calls = {"count": 0}

    def _describe(name):
        describe_calls["count"] += 1
        if describe_calls["count"] == 1:
            return {"repository": {}}
        return {"repository": {"name": name, "online": True}}

    monkeypatch.setattr(nexus3_repositories, "describe", _describe)

    ret = nexus3_repositories.proxy(
        name="docker-proxy-a",
        repository_format="docker",
        remote_url="https://registry-1.docker.io",
        docker_path_enabled=True,
        docker_subdomain="docker-proxy-a",
        remote_auth_type="username",
        remote_username="user",
        remote_password="pass",
    )

    assert ret["repository"]["name"] == "docker-proxy-a"

    method, path, payload = client.calls[0]
    assert method == "post"
    assert path == "v1/repositories/docker/proxy"
    assert payload["docker"]["pathEnabled"] is True
    assert payload["docker"]["subdomain"] == "docker-proxy-a"
    assert payload["httpClient"]["authentication"]["type"] == "username"


def test_proxy_update_path_for_existing_repository(monkeypatch):
    client = _Client(
        {("put", "v1/repositories/docker/proxy/docker-proxy-a"): {"status": 204, "body": ""}}
    )
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)

    describe_calls = {"count": 0}

    def _describe(name):
        describe_calls["count"] += 1
        if describe_calls["count"] == 1:
            return {"repository": {"name": name}}
        return {"repository": {"name": name, "online": True}}

    monkeypatch.setattr(nexus3_repositories, "describe", _describe)

    ret = nexus3_repositories.proxy(
        name="docker-proxy-a",
        repository_format="docker",
        remote_url="https://registry-1.docker.io",
    )

    assert ret["repository"]["name"] == "docker-proxy-a"
    assert client.calls[0][0] == "put"
    assert client.calls[0][1] == "v1/repositories/docker/proxy/docker-proxy-a"


def test_group_create_uses_maven_path_and_members(monkeypatch):
    client = _Client({("post", "v1/repositories/maven/group"): {"status": 201, "body": ""}})
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)

    describe_calls = {"count": 0}

    def _describe(name):
        describe_calls["count"] += 1
        if describe_calls["count"] == 1:
            return {"repository": {}}
        return {"repository": {"name": name, "group": {"memberNames": ["repo-a"]}}}

    monkeypatch.setattr(nexus3_repositories, "describe", _describe)

    ret = nexus3_repositories.group(
        name="group-a",
        repository_format="maven2",
        group_members=["repo-a"],
    )

    assert ret["repository"]["name"] == "group-a"
    method, path, payload = client.calls[0]
    assert method == "post"
    assert path == "v1/repositories/maven/group"
    assert payload["group"]["memberNames"] == ["repo-a"]


def test_group_update_error_sets_error_payload(monkeypatch):
    client = _Client(
        {("put", "v1/repositories/docker/group/group-a"): {"status": 500, "body": "nope"}}
    )
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)
    monkeypatch.setattr(
        nexus3_repositories, "describe", lambda _name: {"repository": {"name": "group-a"}}
    )

    ret = nexus3_repositories.group(
        name="group-a",
        repository_format="docker",
        group_members=["repo-a"],
    )

    assert "could not update repository" in ret["comment"]
    assert ret["error"]["code"] == 500


def test_hosted_create_yum_payload(monkeypatch):
    client = _Client({("post", "v1/repositories/yum/hosted"): {"status": 201, "body": ""}})
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)

    describe_calls = {"count": 0}

    def _describe(name):
        describe_calls["count"] += 1
        if describe_calls["count"] == 1:
            return {"repository": {}}
        return {"repository": {"name": name, "yum": {"repodataDepth": 3}}}

    monkeypatch.setattr(nexus3_repositories, "describe", _describe)

    ret = nexus3_repositories.hosted(
        name="yum-hosted-a",
        repository_format="yum",
        yum_repodata_depth=3,
        yum_deploy_policy="permissive",
    )

    assert ret["repository"]["name"] == "yum-hosted-a"
    method, path, payload = client.calls[0]
    assert method == "post"
    assert path == "v1/repositories/yum/hosted"
    assert payload["yum"]["repodataDepth"] == 3
    assert payload["yum"]["deployPolicy"] == "PERMISSIVE"


def test_hosted_update_error_sets_error_payload(monkeypatch):
    client = _Client(
        {("put", "v1/repositories/docker/hosted/docker-hosted-a"): {"status": 400, "body": "bad"}}
    )
    monkeypatch.setattr(nexus3_repositories.nexus3, "NexusClient", lambda: client)
    monkeypatch.setattr(
        nexus3_repositories,
        "describe",
        lambda _name: {"repository": {"name": "docker-hosted-a"}},
    )

    ret = nexus3_repositories.hosted(
        name="docker-hosted-a",
        repository_format="docker",
        docker_http_port=5000,
    )

    assert "could not update repository" in ret["comment"]
    assert ret["error"]["code"] == 400
