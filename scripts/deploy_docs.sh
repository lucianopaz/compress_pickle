#!/usr/bin/env bash

set -ex # fail on first error, print commands

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

git checkout -b master
eval "${DIR}/make_docs.sh"
cd "${DIR}/../docs"
git add html
git commit -m "Documentation built by Travis CD (id $TRAVIS_BUILD_NUMBER)"
eval "${DIR}/push_docs.sh"
