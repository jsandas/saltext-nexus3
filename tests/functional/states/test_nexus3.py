import pytest

pytestmark = [
    pytest.mark.requires_salt_states("nexus3.exampled"),
]


@pytest.fixture
def nexus3(states):
    return states.nexus3


def test_replace_this_this_with_something_meaningful(nexus3):
    echo_str = "Echoed!"
    ret = nexus3.exampled(echo_str)
    assert ret.result
    assert not ret.changes
    assert echo_str in ret.comment
