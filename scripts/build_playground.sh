#!/usr/bin/env bash
# Build the unitcorn wheel and put it beside the playground page.
#
#   scripts/build_playground.sh
#   python -m http.server -d docs/playground 8000     # then open http://localhost:8000/
#
# The page installs this wheel into Pyodide, so what it shows is the code in this checkout. The wheel is
# not committed (see .gitignore); publish the folder with the wheel in it.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist/playground-build
poetry build -f wheel -o dist/playground-build
rm -f docs/playground/unitcorn-*.whl
cp dist/playground-build/unitcorn-*-py3-none-any.whl docs/playground/
ls -1 docs/playground/unitcorn-*.whl
