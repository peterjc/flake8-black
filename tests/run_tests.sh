#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Assumes in the tests/ directory

echo "Checking we report no errors on these test cases"
flake8 --select BLK test_cases/*.py
flake8 --select BLK --max-line-length 50 test_cases/*.py
flake8 --select BLK --max-line-length 90 test_cases/*.py
flake8 --select BLK with_pyproject_toml/*.py
flake8 --select BLK --max-line-length 88 with_pyproject_toml/
flake8 --select BLK non_conflicting_configurations/*.py
flake8 --select BLK conflicting_configurations/*.py

echo "Checking we report expected black changes"
diff test_changes/hello_world.txt <(flake8 --select BLK test_changes/hello_world.py)
diff test_changes/hello_world_EOF.txt <(flake8 --select BLK test_changes/hello_world_EOF.py)

echo "Tests passed."
