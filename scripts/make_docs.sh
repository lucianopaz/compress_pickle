#!/usr/bin/env bash

set -e # fail on first error, print commands

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/../docs"
make html
