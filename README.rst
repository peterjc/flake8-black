flake8-black
============

.. image:: https://img.shields.io/pypi/v/flake8-black.svg
   :alt: Released on the Python Package Index (PyPI)
   :target: https://pypi.python.org/pypi/flake8-black
.. image:: https://img.shields.io/travis/peterjc/flake8-black/master.svg
   :alt: Testing with TravisCI
   :target: https://travis-ci.org/peterjc/flake8-black/branches
.. image:: https://img.shields.io/pypi/dm/flake8-black.svg
   :alt: PyPI downloads
   :target: https://pypistats.org/packages/flake8-black
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :alt: Code style: black
   :target: https://github.com/python/black

Introduction
------------

This is an MIT licensed `flake8 <https://gitlab.com/pycqa/flake8>`_ plugin
for validating Python code style with the command line code formatting tool
`black <https://github.com/python/black>`_. It is available to install from
the Python Package Index (PyPI):

- https://pypi.python.org/pypi/flake8-black

Black, *"The Uncompromising Code Formatter"*, is normally run to edit your
Python code in place to match their coding style, a strict subset of the
`PEP 8 style guide <https://www.python.org/dev/peps/pep-0008/>`_.

The point of this plugin is to be able to run ``black --check ...`` from
within the ``flake8`` plugin ecosystem. You might use this via a ``git``
pre-commit hook, or as part of your continuous integration testing.

Flake8 Validation codes
-----------------------

Early versions of flake8 assumed a single character prefix for the validation
codes, which became problematic with collisions in the plugin ecosystem. Since
v3.0, flake8 has supported longer prefixes, therefore this plugin uses ``BLK``
as its prefix.

====== =======================================================================
Code   Description
------ -----------------------------------------------------------------------
BLK100 Black would make changes.
BLK8## Configuration error (various):
BLK800 Conflicting line length in flake8 and black settings.
BLK9## Internal error (various):
BLK900 Failed to load file: ...
BLK901 Invalid input.
BLK998 Could not access flake8 line length setting.
BLK999 Unexpected exception.
====== =======================================================================

Note that if your Python code has a syntax error, ``black --check ...`` would
report this as an error. Likewise ``flake8 ...`` will by default report the
syntax error, but importantly it does not seem to then call the plugins, so
you will *not* get an additional ``BLK`` error.


Installation
------------

Python 3.6 or later is required to run ``black``, so that is recommended, but
``black`` can be used on Python code written for older versions of Python.

Install ``flake8-black`` using ``pip``, which should install ``flake8`` and
``black`` as well if not already present::

    $ pip install flake8-black

The new validator should be automatically included when using ``flake8`` which
may now report additional validation codes starting with ``BLK`` (as defined
above). For example::

    $ flake8 example.py

You can request only the ``BLK`` codes be shown using::

    $ flake8 --select BLK example.py


Configuration
-------------

We recommend using the following settings in your ``flake8`` configuration,
for example in your ``.flake8``  file::

    [flake8]
    # Recommend matching the black default line length of 88,
    # rather than the flake8 default of 79:
    max-line-length = 88
    extend-ignore =
        # See https://github.com/PyCQA/pycodestyle/issues/373
        E203,

In order not to trigger flake8's ``E501 line too long`` errors, the plugin
passes the ``flake8`` maximum line length when it calls ``black``,
equivalent to doing ``black -l 88 --check *.py`` at the command line.

Note currently ``pycodestyle`` gives false positives on the spaces ``black``
uses for slices, which ``flake8`` reports as ``E203: whitespace before ':'``.
Until `pyflakes issue 373 <https://github.com/PyCQA/pycodestyle/issues/373>`_
is fixed, and ``flake8`` is updated, we suggest disabling this style check.

If you are using custom value of maximum line length parameter, check that black configuration (pyproject.toml) and
flake8 configuration (.flake8) use the same value. Otherwise, you will get BLK997 error.

Ignoring validation codes
-------------------------

Using the flake8 no-quality-assurance pragma comment is not recommended
(e.g. adding ``# noqa: BLK100`` to the first line black would change).
Instead use the black pragma comments ``# fmt: off`` at the start, and
``# fmt: on`` at the end, of any region of your code which should not be
changed.


Version History
---------------

======= ============ ===========================================================
Version Release date   Changes
------- ------------ -----------------------------------------------------------
v0.0.4  2019-03-15   - Supports black 19.3b0 which changed a function call.
v0.0.3  2019-02-21   - Bug fix when ``W292 no newline at end of file`` applies,
                       contribution from
                       `Sapphire Becker <https://github.com/sapphire-janrain>`_.
v0.0.2  2019-02-15   - Document syntax error behaviour (no BLK error reported).
v0.0.1  2019-01-10   - Initial public release.
                     - Passes ``flake8`` max-line-length setting to ``black``.
======= ============ ===========================================================


Developers
----------

This plugin is on GitHub at https://github.com/peterjc/flake8-black

To make a new release once tested locally and on TravisCI::

    $ git tag vX.Y.Z
    $ python setup.py sdist --formats=gztar
    $ twine upload dist/flake8-black-X.Y.Z.tar.gz
    $ git push origin master --tags
