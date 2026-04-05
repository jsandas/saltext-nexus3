#!/usr/bin/env python3

import pprint
import sys

import salt.client

client = salt.client.LocalClient()

pp = pprint.PrettyPrinter(indent=2)


## Modules Integration Tests ##
test_data = {
    "test_blobstore": {
        "inputs": [],
        "results": {"type": "File"},
    },
    "test_s3_blobstore": {
        "inputs": [
            "store_type=s3",
            "s3_bucket=nexus3",
            "s3_access_key_id=AKIAIOSFODNN7EXAMPLE",
            "s3_secret_access_key=wJalrXUtnFEMIK7MDENGbPxRfiCYEXAMPLEKEY",
            "s3_endpoint=http://minio:9000",
            "s3_force_path_style=True",
        ],
        "results": {"type": "S3"},
    },
}

blobstores = []


def test_create_blobstore():
    for name, values in test_data.items():
        # print(" Creating blobstore {}".format(name))
        try:
            _create_blobstore(name, values)
            blobstores.append(name)
        except:
            print(f" Failed creating blobstore {name}")


def _create_blobstore(name, values):
    list1 = [name]
    args = list1 + values["inputs"]

    ret = client.cmd("test.minion", "nexus3_blobstores.create", args)
    # print(ret)
    assert ret["test.minion"]["blobstore"] != {}, "blobstore is empty"
    assert ret["test.minion"]["blobstore"]["name"] == name, f"blobstore {name} not created"
    assert (
        ret["test.minion"]["blobstore"]["type"] == values["results"]["type"]
    ), "wrong store type {} found".format(values["results"]["type"])


def test_list_blobstores():
    ret = client.cmd("test.minion", "nexus3_blobstores.list_all")
    # print(ret)
    count = len(blobstores)
    assert ret["test.minion"]["blobstores"] != {}, "data is empty"
    assert len(ret["test.minion"]["blobstores"]) != count, "blobstore count {}, expected {}".format(
        len(ret["test.minion"]["blobstores"]), count
    )


def test_delete_blobstore():
    for name in blobstores:
        # print(" Deleting blobstore {}".format(name))
        _delete_blobstore(name)


def _delete_blobstore(blobstore):
    ret = client.cmd("test.minion", "nexus3_blobstores.delete", [f"name={blobstore}"])
    # print(ret)
    assert (
        ret["test.minion"]["comment"] == f'Deleted blobstore "{blobstore}"'
    ), f"blobstore {blobstore} not deleted"


## States Integration Tests ##
state_test_data = {
    "pillar": {
        "nexus3": {
            "blobstores": {
                "apt": [],
                "docker": [],
                "maven": [{"quota_type": "spaceRemainingQuota"}, {"quota_limit": 1000000000}],
                "s3blobstore": [
                    {"store_type": "s3"},
                    {"s3_bucket": "nexus3"},
                    {"s3_access_key_id": "AKIAIOSFODNN7EXAMPLE"},
                    {"s3_secret_access_key": "wJalrXUtnFEMIK7MDENGbPxRfiCYEXAMPLEKEY"},
                    {"s3_endpoint": "http://minio:9000"},
                    {"s3_force_path_style": True},
                ],
                "unwanted-blobstore": [],
            },
        }
    },
    "results": {
        "apt": {
            "result": True,
            "changes": {"type": "File", "softQuota": None},
            "comment": "",
        },
        "docker": {
            "result": True,
            "changes": {"type": "File", "softQuota": None},
            "comment": "",
        },
        "maven": {
            "result": True,
            "changes": {
                "type": "File",
                "softQuota": {"limit": 1000000000, "type": "spaceRemainingQuota"},
            },
            "comment": "",
        },
        "s3blobstore": {
            "result": True,
            "changes": {
                "type": "S3",
                "softQuota": None,
            },
            "comment": "",
        },
    },
}


def test_blobstores_state():
    pillar = state_test_data["pillar"]
    # pp.pprint(pillar)
    ret = client.cmd("test.minion", "state.apply", ["nexus3.blobstores", f"pillar={pillar}"])
    # pp.pprint(ret['test.minion'])
    for key, values in state_test_data["results"].items():
        id = f"nexus3_blobstores_|-create_blobstore_{key}_|-{key}_|-present"
        output = ret["test.minion"][id]
        assert values["result"] == output["result"], (
            f"[{key}] wrong state result! expected: \"{values['result']}\" got: \"{output['result']}\"\n"
            f"  comment: {output['comment']}\n"
            f"  changes: {output['changes']}"
        )
        assert (
            values["comment"] == output["comment"]
        ), f"[{key}] wrong state comment! expected: \"{values['comment']}\" got: \"{output['comment']}\""
        assert (
            values["changes"]["type"] == output["changes"]["blobstore"]["type"]
        ), f"[{key}] wrong type result! expected: \"{values['changes']['type']}\" got: \"{output['changes']['blobstore']['type']}\""
        assert (
            values["changes"]["softQuota"] == output["changes"]["blobstore"]["softQuota"]
        ), f"[{key}] wrong softQuota! expected: \"{values['changes']['softQuota']}\" got: \"{output['changes']['blobstore']['softQuota']}\""


state_test_data2 = {
    "pillar": {
        "nexus3": {
            "blobstores": {
                "maven": [{"quota_type": "spaceRemainingQuota"}, {"quota_limit": 2000000000}],
            },
        }
    },
    "results": {
        "maven": {
            "result": None,
            "comment": "blobstore maven will be updated with: {'quota_limit': 2000000000}",
        },
    },
}


def test_blobstores_state2():
    pillar = state_test_data2["pillar"]
    # # pp.pprint(pillar)
    ret = client.cmd(
        "test.minion", "state.apply", ["nexus3.blobstores", f"pillar={pillar}", "test=True"]
    )
    # pp.pprint(ret['test.minion'])
    for key, values in state_test_data2["results"].items():
        id = f"nexus3_blobstores_|-create_blobstore_{key}_|-{key}_|-present"
        output = ret["test.minion"][id]
        assert (
            values["result"] == output["result"]
        ), f"wrong state result! expected: \"{values['result']}\" got: \"{output['result']}\""
        assert (
            values["comment"] == output["comment"]
        ), f"wrong state comment! expected: \"{values['comment']}\" got: \"{output['comment']}\""
