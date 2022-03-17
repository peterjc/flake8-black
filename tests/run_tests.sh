#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Assumes in the tests/ directory

echo "Checking our configuration option appears in help"
flake8 -h 2>&1 | grep "black-config"

set +o pipefail

echo "Checking we report an error when can't find specified config file"
flake8 --black-config does_not_exist.toml 2>&1 | grep -i "could not find"

echo "Checking failure with mal-formed TOML file"
flake8 --select BLK test_cases/ --black-config with_bad_toml/pyproject.toml 2>&1 | grep -i "could not parse"

set -o pipefail

echo "Checking we report no errors on these test cases"
# Must explicitly include *.pyi or flake8 ignores them
flake8 --select BLK test_cases/*.py*
# Adding --black-config '' meaning ignore any pyproject.toml should have no effect:
flake8 --select BLK test_cases/*.py --black-config ''
flake8 --select BLK --max-line-length 50 test_cases/*.py
flake8 --select BLK --max-line-length 90 test_cases/*.py
flake8 --select BLK with_pyproject_toml/*.py
flake8 --select BLK with_pyproject_toml/*.py --black-config with_pyproject_toml/pyproject.toml
flake8 --select BLK --max-line-length 88 with_pyproject_toml/
flake8 --select BLK without_pyproject_toml/*.py --black-config with_pyproject_toml/pyproject.toml
# Adding --black-config '' should have no effect:
#flake8 --select BLK --max-line-length 88 with_pyproject_toml/ --black-config ''
flake8 --select BLK non_conflicting_configurations/*.py
flake8 --select BLK conflicting_configurations/*.py
# Here using --black-config '' meaning ignore any (bad) pyproject.toml files:
flake8 --select BLK with_bad_toml/hello_world.py --black-config ''

echo "Checking we report expected black changes"
diff test_changes/hello_world.txt <(flake8 --select BLK test_changes/hello_world.py)
diff test_changes/hello_world_EOF.txt <(flake8 --select BLK test_changes/hello_world_EOF.py)
diff test_changes/hello_world_EOF.txt <(flake8 --select BLK test_changes/hello_world_EOF.py --black-config '')
diff <(
  if [ "${WIN:-1}" = 0 ]; then
    sed 's_/_\\_2' with_bad_toml/hello_world.txt
  else
    cat with_bad_toml/hello_world.txt
  fi
) <(flake8 --select BLK with_bad_toml/hello_world.py)
diff with_pyproject_toml/ignoring_toml.txt <(flake8 with_pyproject_toml/ --select BLK --black-config '')

# no changes by default,
flake8 --select BLK test_changes/commas.py tests/black_preview.py
# will make changes if we ignore the magic trailing comma:
diff test_changes/commas.txt <(flake8 --select BLK test_changes/commas.py --black-config with_pyproject_toml/pyproject.toml)
# will make changes if we enable future functionality preview mode:
diff test_changes/black_preview.txt <(flake8 --select BLK test_changes/black_preview.py --black-config with_pyproject_toml/pyproject.toml)

echo "Tests passed."
