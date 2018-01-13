#!/usr/bin/env bash

# Note: script must be executed from project root directory
PROJECT_DIR=$PWD

echo "Creating zip file at $PROJECT_DIR/deploy.zip"

# Check if virtualenv is active
echo $PATH | grep -q venv; venv=$?

# Activate virtualenv if not already active
if [[ $venv -ne 0 ]]; then
  source venv/bin/activate
fi

PKGS=$PROJECT_DIR/venv/lib/python3.5/site-packages
echo "Zipping project dependencies at $PKGS..."
cd $PKGS && zip -r9 -q $PROJECT_DIR/deploy.zip *

echo "Zipping application files..."
cd $PROJECT_DIR && find ./app -name "*.py" -print | zip -gq deploy.zip -@

# Deactivate virtualenv if not active on execution
if [[ $venv -ne 0 ]]; then
  deactivate
fi

echo "Done."
