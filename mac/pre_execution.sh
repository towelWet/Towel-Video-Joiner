#!/bin/bash
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

# Ensure Python will use correct relative paths
BASEDIR=$(dirname "$0")
/usr/local/bin/python3 "$BASEDIR/../Resources/main.py"