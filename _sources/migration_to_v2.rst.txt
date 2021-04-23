#######################
Migration to v2 from v1
#######################

==============
v2.0 changelog
==============

The main changes coming with v2.0 are:

- name's changing from Nautilus Connectors Kit to Artefactory Connectors Kit. All references to NCK have been changed to ACK.

- a new entrypoint using a json config file for commands to avoid very long command lines: ``ack/entrypoints/json/main.py``. It takes the config file's path as an argument with ``--config-file``:

.. code-block:: shell

    python ack/entrypoints/json/main.py --config-file path/to/file.json

- change of the cli entrypoint's path from ``nck/entrypoint.py`` to ``ack/entrypoints/cli/main.py``:

.. code-block:: shell

    python ack/entrypoints/cli/main.py reader --option-name option writer --option-name option

- support only by Python 3.8 and by more recent versions to fully use Typing library

==============
How to migrate
==============

1. Pull the `dev` branch from the `GitHub repository <https://github.com/artefactory/artefactory-connectors-kit/tree/dev>`__ if you already set-up your environment:

.. code-block:: shell

    git pull origin dev

2. If your virtual environment is running Python 3.7 or less, you need to recreate it (you can test it with ``python -V`` in your virtualenv). **If it's running Python 3.8 or more, you can pass to step 3**.

Your first need to be sure that your ``python3 -V`` gives version 3.8 or more. If not, you need to install a more recent Python version. Then, do:

.. code-block:: shell

    rm -rf ack-env
    python3 -m venv ack-env
    source ack-env/bin/activate

3. Install/update the dependencies:

.. code-block:: shell

    pip install -r requirements.txt
    pip install -r requirements-dev.text

4. Change the entrypoint's path of all your commands from ``nck/entrypoint.py`` to ``ack/entrypoints/cli/main.py``. If you wish, you can also convert your commands into a json config file following the documentation in the :ref:`ackwithjson` section.
