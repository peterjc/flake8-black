#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Print 'Hello world' to the terminal (with syntax error).

This is a simple test script using a hashbang line and a PEP263 encoding line. There is
a deliberate syntax error (missing closing bracket).

Black will fail to parse this file:

    $ black --check no_closing_bracket.py ; echo "Return code $?"
    error: cannot format no_closing_bracket.py: ('EOF in multi-line statement', (31, 0))
    All done! ð ð ð
    1 file would fail to reformat.
    Return code 123

It seems in this case the plugin never gets the chance to report:

    $ flake8 --select BLK no_closing_bracket.py ; echo "Return code $?"
    Return code 0

This doesn't really matter, as it would be redundant with the flake8 syntax errors:

    $ flake8 no_closing_bracket.py ; echo "Return code $?"
    no_closing_bracket.py:30:19: E999 SyntaxError: unexpected EOF while parsing
    Return code 1

"""

print("Hello world"
