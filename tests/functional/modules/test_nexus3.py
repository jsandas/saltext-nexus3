import pytest

pytestmark = [
    pytest.mark.requires_salt_modules("nexus3.example_function"),
]


@pytest.fixture
def nexus3(modules):
    return modules.nexus3


def test_replace_this_this_with_something_meaningful(nexus3):
    echo_str = "Echoed!"
    res = nexus3.example_function(echo_str)
    assert res == echo_str
