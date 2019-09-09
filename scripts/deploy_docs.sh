#!/usr/bin/env bash

set -e # fail on first error, print commands

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

git checkout -b master
eval "${DIR}/make_docs"
cd "${DIR}/../docs"
git add html
git commit -m "Documentation built by Travis CD (id $TRAVIS_BUILD_NUMBER)"
git remote add origin-pages https://${GITHUB_TOKEN}@github.com/lucianopaz/compress_pickle.git >/dev/null 2>&1
git push --quiet --set-upstream origin-pages master

