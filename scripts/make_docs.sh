#!/usr/bin/env bash

set -ex # fail on first error, print commands

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/../docs"
printf "Making html docs\n";
make html
printf "\033[1;34mDocumentation html correctly built!\033[0m\n\n";
