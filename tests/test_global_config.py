from pathlib import Path

import flake8_black


def test_global_config(fs):
    home = Path.home() / ".config/flake8-black/pyproject.toml"
    fs.create_file(home, contents="[tool.black]\nskip-string-normalization = true\n")

    bl = flake8_black.BlackStyleChecker("foo", "tests/test_changes/hello_world.py")
    assert bl._load_black_config() == {'skip_string_normalization': True}
