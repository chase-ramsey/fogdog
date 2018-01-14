#!/usr/bin/env bash

# Note: script must be executed from project root directory
PROJECT_DIR=$PWD

if [[ -r $PROJECT_DIR/deploy.zip ]]; then
  rm $PROJECT_DIR/deploy.zip
fi
echo "Creating zip file at $PROJECT_DIR/deploy.zip"

# Check if virtualenv is active
echo $PATH | grep -q venv; venv=$?

# Activate virtualenv if not already active
if [[ $venv -ne 0 ]]; then
  source venv/bin/activate
fi

PKGS=$VIRTUAL_ENV/lib/python3.5/site-packages
echo "Zipping project dependencies at $PKGS..."
cd $PKGS && zip -r9 -q $PROJECT_DIR/deploy.zip *

echo "Zipping application files..."
cd $PROJECT_DIR/app && find . -name "*.py" -print | zip -gq $PROJECT_DIR/deploy.zip -@

echo 'Updating function code on AWS...'
aws lambda update-function-code --function-name fogdog_bark --zip-file fileb://$PROJECT_DIR/deploy.zip

# Deactivate virtualenv if not active on execution
if [[ $venv -ne 0 ]]; then
  deactivate
fi

echo "Done."
