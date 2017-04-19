#!/bin/sh
# flake8 --max-line-length=180 /src/
cd /src
python -m 'pytest' /src/tests/ "$@"
