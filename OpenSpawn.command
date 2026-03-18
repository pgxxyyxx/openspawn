#!/bin/bash
set -euo pipefail

cd "/Users/petergratzke/projects/openspawn/prototype"
"$PWD/.venv/bin/python" -m openspawn "$@"
