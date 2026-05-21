#!/bin/bash

# ---------------------------------------------------------------------------
# File: make_release.bash
# Author: Brigitte Bigi
# Date: 
# Brief: AViSS packaging script.
# ---------------------------------------------------------------------------

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROGRAM_NAME="AViSS"
PROGRAM_VERSION=$(grep -e '__version__ =' $HERE/aviss/__init__.py | awk -F'=' '{print $2}' | cut -f2 -d'"')
PACKAGE_NAME=`pwd`/${PROGRAM_NAME}-${PROGRAM_VERSION}.zip

echo "Create release for AViSS - "$PROGRAM_VERSION

echo "Create documentation"
python makedoc.py

echo "Delete any __pycache__ folder"
  for pycache in `find . -name "__pycache__"`;
  do
    rm -rf $pycache;
  done

echo "Create 'zip' archive" $PACKAGE_NAME
  zip -q -r $PACKAGE_NAME aviss tests docs pyproject.toml *.py *.md *.cff
  if [ "$?" != 0 ]; then
      echo -e "${RED}No package created!${NC}"
      popd
      return 1
  else
      popd
      echo "  The file" $PACKAGE_NAME "has been created."
  fi

echo "Create wheel"
python -m build

# transfert to pypi.org:
# .venv/bin/twine upload -r pypi dist/aviss-0.X-py3-none-any.whl
