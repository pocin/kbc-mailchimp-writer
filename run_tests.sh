#!/bin/sh
# flake8 --max-line-length=180 /src/
source /src/tests/env.sh
cd /src
python3 -m 'pytest' /src/tests/ "$@"
