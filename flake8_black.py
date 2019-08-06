"""Check Python code passes black style validation via flake8.

This is a plugin for the tool flake8 tool for checking Python
soucre code using the tool black.
"""

from os import path
from pathlib import Path

import black
import toml

from flake8 import utils as stdin_utils
from flake8 import LOG


__version__ = "0.1.1"

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

    STDIN_NAMES = {"stdin", "-", "(none)", None}

    # Black settings
    line_length = black.DEFAULT_LINE_LENGTH  # Expect to be 88
    target_versions = set()
    skip_string_normalization = False

    # Which TOML have we loaded, and why?
    toml_filename = None
    toml_override = False

    def __init__(self, tree, filename="(none)", builtins=None):
        """Initialise."""
        self.tree = tree
        self.filename = filename
        # Following for legacy versions of black only,
        # see property self._file_mode for new black versions:
        self.file_mode = 0  # was: black.FileMode.AUTO_DETECT

    def _update_black_config(self):
        """Find and load any local pyproject.toml with black config."""
        source_path = (
            self.filename
            if self.filename not in self.STDIN_NAMES
            else Path.cwd().as_posix()
        )
        project_root = black.find_project_root((Path(source_path),))
        path = project_root / "pyproject.toml"

        if path.is_file():
            # Use this pyproject.toml for this python file,
            # (unless configured with global override config)
            self.load_black_toml(path, override=False)

    @classmethod
    def load_black_toml(cls, toml_filename, override=False):
        """Load specified black configuration from TOML file."""
        if not toml_filename:
            if override:
                cls.toml_filename = None
                cls.toml_override = True
            return
        if cls.toml_filename == toml_filename:
            LOG.info(
                "flake8-black: already loaded black settings from %s", cls.toml_filename
            )
            return
        elif override:
            cls.toml_override = True
            # Continue below...
        elif cls.toml_filename:
            LOG.info(
                "flake8-black: ignoring %s in favour of %s",
                toml_filename,
                cls.toml_filename,
            )
            return
        elif cls.toml_override:
            LOG.info(
                "flake8-black: ignoring %s as explicitly using no black config",
                toml_filename,
            )
            return

        LOG.info("flake8-black: loading black settings from %s", toml_filename)
        cls.toml_filename = toml_filename
        pyproject_toml = toml.load(str(toml_filename))
        config = pyproject_toml.get("tool", {}).get("black", {})
        black_config = {
            k.replace("--", "").replace("-", "_"): v for k, v in config.items()
        }

        cls.target_versions = {
            black.TargetVersion[val.upper()]
            for val in black_config.get("target_version", [])
        }
        cls.line_length = black_config.get("line_length", cls.line_length)
        cls.skip_string_normalization = black_config.get(
            "skip_string_normalization", False
        )

    @property
    def _file_mode(self):
        """Generate black.FileMode object (or set legacy alternative)."""
        # Check for a local pyproject.toml
        self._update_black_config()

        if self.skip_string_normalization:
            # Used with older versions of black:
            self.file_mode |= 4  # was black.FileMode.NO_STRING_NORMALIZATION
        try:
            # Recent versions of black have a FileMode object
            # which includes the line length setting
            return black.FileMode(
                target_versions=self.target_versions,
                line_length=self.line_length,
                string_normalization=not self.skip_string_normalization,
            )
        except TypeError as e:
            # Legacy mode for old versions of black
            assert "got an unexpected keyword argument" in str(e), e
            return None

    @classmethod
    def add_options(cls, parser):
        """Adding black-config option."""
        parser.add_option(
            "--black-config",
            default="",
            action="store",
            type="string",
            parse_from_config=True,
            help="Path to black configuration file "
            "(overrides the default pyproject.toml; "
            "use - to force using no config file)",
        )

    @classmethod
    def parse_options(cls, options):
        """Adding black-config option."""
        # We have one and only one flake8 plugin configuration
        if not options.black_config:
            LOG.info("flake8-black: No black configuration set")
            return
        elif options.black_config == "-":
            LOG.info("flake8-black: Explicitly using no black TOML file")
            cls.load_black_toml(None, override=True)
            return

        # Validate the path setting - handling relative paths
        black_config_path = Path(options.black_config)
        if options.config:
            # Assume black config path was via flake8 config file
            base_path = Path(path.dirname(path.abspath(options.config)))
            black_config_path = base_path / black_config_path
        if not black_config_path.is_file():
            raise ValueError(
                "Plugin flake8-black could not find specified black config file: "
                "--black-config %s" % black_config_path
            )

        # Now load the TOML file, and the black section within it
        # This configuration is to override any local pyproject.toml
        try:
            cls.load_black_toml(black_config_path, override=True)
        except toml.decoder.TomlDecodeError:
            # Could raise BLK997, but view this as an abort condition
            raise ValueError(
                "Plugin flake8-black could not parse specified black config file: "
                "--black-config %s" % black_config_path
            )

    def run(self):
        """Use black to check code style."""
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
        elif source:
            # Call black...
            try:
                if self._file_mode is None:
                    # Legacy version of black, 18.9b0 or older
                    new_code = black.format_file_contents(
                        source,
                        line_length=self.line_length,
                        fast=False,
                        mode=black.FileMode(self.file_mode),
                    )
                else:
                    # For black 19.3b0 or later
                    new_code = black.format_file_contents(
                        source, mode=self._file_mode, fast=False
                    )
            except black.NothingChanged:
                return
            except black.InvalidInput:
                msg = "901 Invalid input."
            except toml.decoder.TomlDecodeError:
                msg = "997 Invalid TOML file: %s" % path.relpath(self.toml_filename)
            except Exception as err:
                msg = "999 Unexpected exception: %s" % err
            else:
                assert (
                    new_code != source
                ), "Black made changes without raising NothingChanged"
                line, col = find_diff_start(source, new_code)
                line += 1  # Strange as col seems to be zero based?
                msg = "100 Black would make changes."
        # If we don't know the line or column numbers, leaving as zero.
        yield line, col, black_prefix + msg, type(self)
