"""Check Python code passes black style validation via flake8.

This is a plugin for the tool flake8 tool for checking Python
soucre code using the tool black.
"""
from pathlib import Path

import black
import toml

from flake8 import utils as stdin_utils


__version__ = "0.0.4"

black_prefix = "BLK"


def find_diff_start(old_src, new_src):
    """Find line number and column number where text first differs."""
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
    # Difference at the end of the file...
    return min(len(old_lines), len(new_lines)), 0


class BlackStyleChecker(object):
    """Checker of Python code using black."""

    name = "black"
    version = __version__

    STDIN_NAMES = set(["stdin", "-", "(none)", None])

    def __init__(self, tree, filename="(none)", builtins=None):
        """Initialise."""
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser):
        """Add any plugin configuration options to flake8."""
        # Currently don't have any of our own options, but have this
        # stub defined in order to activate parse_options being called.
        # parser.add_option(
        #     '--black', action='store_true', parse_from_config=True,
        #     help="Should we run the black checks? (Off by default)"
        # )
        pass

    @classmethod
    def parse_options(cls, options):
        """Parse the configuration options given to flake8."""
        # cls.black_check = bool(options.black)
        cls.line_length = int(options.max_line_length)
        # raise ValueError("Line length %r" % options.max_line_length)

    def _load_black_config(self):
        source_path = (
            self.filename
            if self.filename not in self.STDIN_NAMES
            else Path.cwd().as_posix()
        )
        project_root = black.find_project_root((Path(source_path),))
        path = project_root / "pyproject.toml"

        if path.is_file():
            pyproject_toml = toml.load(str(path))
            config = pyproject_toml.get("tool", {}).get("black", {})
            return {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}
        return None

    @property
    def file_mode(self):
        try:
            black_config = self._load_black_config()
            if black_config:
                target_versions = {
                    black.TargetVersion[val.upper()]
                    for val in black_config.get("target_version", [])
                }

                return black.FileMode(
                    target_versions=target_versions,
                    line_length=self.line_length or black_config.get("line_length", 88),
                    string_normalization=not black_config.get(
                        "skip_string_normalization", False
                    ),
                )
            return black.FileMode(line_length=self.line_length)
        except TypeError as e:
            # Legacy mode
            assert "got an unexpected keyword argument" in str(e), e
            return None

    def run(self):
        """Use black to check code style."""
        # if not self.black_check:
        #    return
        msg = None
        line = 0
        col = 0

        try:
            if self.filename in self.STDIN_NAMES:
                self.filename = "stdin"
                source = stdin_utils.stdin_get_value()
            else:
                with open(self.filename, "rb") as buf:
                    source, _, _ = black.decode_bytes(buf.read())
        except Exception as e:
            source = ""
            msg = "900 Failed to load file: %s" % e

        if not source and not msg:
            # Empty file (good)
            return
        elif not self.line_length:
            msg = "998 Could not access flake8 line length setting."
        elif source:
            # Call black...
            try:
                if self.file_mode is None:
                    # Legacy version of black, 18.9b0 or older
                    new_code = black.format_file_contents(
                        source, line_length=self.line_length, fast=False
                    )
                else:
                    # For black 19.3b0 or later
                    new_code = black.format_file_contents(
                        source, mode=self.file_mode, fast=False
                    )
            except black.NothingChanged:
                return
            except black.InvalidInput:
                msg = "901 Invalid input."
            except Exception as e:
                msg = "999 Unexpected exception: %s" % e
            else:
                assert (
                    new_code != source
                ), "Black made changes without raising NothingChanged"
                line, col = find_diff_start(source, new_code)
                line += 1  # Strange as col seems to be zero based?
                msg = "100 Black would make changes."
        # If we don't know the line or column numbers, leaving as zero.
        yield line, col, black_prefix + msg, type(self)
