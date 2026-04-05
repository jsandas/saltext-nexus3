"""
Salt execution module
"""

import logging

log = logging.getLogger(__name__)

__virtualname__ = "nexus3"


def __virtual__():
    # To force a module not to load return something like:
    #   return (False, "The nexus3 execution module is not implemented yet")
    return __virtualname__


def example_function(text):
    """
    This example function should be replaced

    CLI Example:

    .. code-block:: bash

        salt '*' nexus3.example_function text="foo bar"
    """
    return __salt__["test.echo"](text)
