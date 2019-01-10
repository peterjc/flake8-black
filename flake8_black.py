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
        return line, min(len(old), len(new))
    # Difference at the of the file...
    return min(len(old_lines), min(new_lines)), 0


class BlackStyleChecker(object):
    """Checker of Python code using black."""

    name = "black"
    version = __version__

    STDIN_NAMES = set(["stdin", "-", "(none)", None])

    def __init__(self, tree, filename="(none)", builtins=None):
        """Initialise."""
        self.tree = tree
        self.filename = filename
        try:
            self.load_source()
            self.err = None
        except Exception as err:
            self.source = None
            self.err = err

    @classmethod
    def add_options(cls, parser):
        # Currently don't have any of our own options, but have this
        # stub defined in order to activate parse_options being called.
        # parser.add_option(
        #     '--black', action='store_true', parse_from_config=True,
        #     help="Should we run the black checks? (Off by default)"
        # )
        pass

    @classmethod
    def parse_options(cls, options):
        # cls.black_check = bool(options.black)
        cls.line_length = int(options.max_line_length)
        # raise ValueError("Line length %r" % options.max_line_length)

    def run(self):
        """Use black to check code style."""
        # if not self.black_check:
        #    return
        msg = None
        line = 0
        col = 0
        if self.err is not None:
            assert self.source is None
            msg = black_prefix + "900 Failed to load file: %s" % self.err
        elif not self.source:
            # Empty file, nothing to change
            return
            # elif not self.black_check:
            msg = "997 Black disabled"  # hack!
        elif not self.line_length:
            msg = "998 Could not access flake8 line length setting"
        else:
            # Call black...
            try:
                # Set mode?
                new_code = black.format_file_contents(
                    self.source, line_length=self.line_length, fast=False
                )
            except black.NothingChanged:
                return
            except black.InvalidInput:
                msg = "901 Invalid input"
            except Exception as e:
                msg = "999 Unexpected exception: %s" % e
            else:
                assert (
                    new_code != self.source
                ), "Black made changes without raising NothingChanged"
                line, col = find_diff_start(self.source, new_code)
                line += 1  # Strange as col seems to be zero based?
                msg = "100 Black would make changes"
        # If we don't know the line or column numbers, leaving as zero.
        yield line, col, black_prefix + msg, type(self)

    def load_source(self):
        """Load the source for the specified file."""
        if self.filename in self.STDIN_NAMES:
            self.filename = "stdin"
            if sys.version_info[0] < 3:
                self.source = sys.stdin.read()
            else:
                self.source = io.TextIOWrapper(sys.stdin.buffer, errors="ignore").read()
        else:
            with tokenize.open(self.filename) as handle:
                self.source = handle.read()
