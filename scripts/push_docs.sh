#!/usr/bin/env bash

set -e # fail on first error

printf "Adding remote origin\n";
git remote add origin-pages https://${GITHUB_TOKEN}@github.com/lucianopaz/compress_pickle.git >/dev/null 2>&1
git push --quiet --set-upstream origin-pages master
printf "\033[1;34mSuccessfully pushed to github!\033[0m\n\n";
