"""Check Python code passes black style validation via flake8.

This is a plugin for the tool flake8 tool for checking Python
soucre code using the tool black.
"""

import io
import logging
import sys
import tokenize

import black


__version__ = "0.0.1"

log = logging.getLogger(__name__)

black_prefix = "BLK"


def find_diff_start(old_src, new_src):
    old_lines = old_src.split("\n")
    new_lines = new_src.split("\n")

    for line in range(min(len(old_lines), len(new_lines))):
        old = old_lines[line]
        new = new_lines[line]
        if old == new:
            continue
        for col in range(min(len(old), len(new))):
            if old[col] != new[col]:
                return line, col
        # Difference at the end of the line...
        return line, min(len(old), len(new)) + 1
    # Difference at the of the file...
    return min(len(old_lines), min(new_lines)) + 1, 0
            

class BlackStyleChecker(object):
    """Checker of Python code using black."""

    name = "black"
    version = __version__

    STDIN_NAMES = set(['stdin', '-', '(none)', None])

    def __init__(self, tree, filename='(none)', builtins=None):
        """Initialise."""
        self.tree = tree
        self.filename = filename
        try:
            self.load_source()
            self.err = None
        except Exception as err:
            self.source = None
            self.err = err
        # TODO, read flake8 config
        self.line_length = 79

    def run(self):
        """Use black to check code style."""
        # Is there any reason not to call load_source here?
        msg = None
        line = 0
        col = 0
        if self.err is not None:
            assert self.source is None
            msg = black_prefix + "900 Failed to load file: %s" % self.err
            yield 0, 0, msg, type(self)
        elif not self.source:
            # Empty file, nothing to change
            pass
        else:
            # Call black...
            try:
                # Set mode?
                new_code = black.format_file_contents(
                    self.source,
                    line_length=self.line_length,
                    fast=False)
            except black.NothingChanged:
                pass
            except black.InvalidInput:
                msg = "901 Invalid input"
            except Exception as e:
                msg = "999 Unexpected exception: %s" % e
            else:
                assert new_code != self.source, \
                    "Black made changes without raising NothingChanged"
                line, col = find_diff_start(self.source, new_code)
                msg = "100 Black would make changes"
        if msg:
            # If we don't know the line or column numbers, leaving as zero.
            yield line, col, black_prefix + msg, type(self)

    def load_source(self):
        """Load the source for the specified file."""
        if self.filename in self.STDIN_NAMES:
            self.filename = 'stdin'
            if sys.version_info[0] < 3:
                self.source = sys.stdin.read()
            else:
                self.source = io.TextIOWrapper(sys.stdin.buffer,
                                               errors='ignore').read()
        else:
            with tokenize.open(self.filename) as handle:
                self.source = handle.read()
