# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Nexus3 extension:
  pip.installed:
    - name: saltext-nexus3
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-nexus3
```
:::

:::{tab} Regular installation
```bash
pip install saltext-nexus3
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
