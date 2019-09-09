#!/usr/bin/env bash

set -e # fail on first error

git remote add origin-pages https://${GITHUB_TOKEN}@github.com/lucianopaz/compress_pickle.git >/dev/null 2>&1
git push --quiet --set-upstream origin-pages master
