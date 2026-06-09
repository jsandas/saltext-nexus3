import pytest
import salt.modules.test as testmod

import saltext.nexus3.modules.nexus3_mod as nexus3_module
import saltext.nexus3.states.nexus3_mod as nexus3_state


@pytest.fixture
def configure_loader_modules():
    return {
        nexus3_module: {
            "__salt__": {
                "test.echo": testmod.echo,
            },
        },
        nexus3_state: {
            "__salt__": {
                "nexus3.example_function": nexus3_module.example_function,
            },
        },
    }


def test_replace_this_this_with_something_meaningful():
    echo_str = "Echoed!"
    expected = {
        "name": echo_str,
        "changes": {},
        "result": True,
        "comment": f"The 'nexus3.example_function' returned: '{echo_str}'",
    }
    assert nexus3_state.exampled(echo_str) == expected
