#!/usr/bin/env bash

set -ex # fail on first error, print commands

if [ ! -z ${TEST_STYLE} ]
then
    printf "Checking code style with black...\n";
    black --check compress_pickle;
    printf "\033[1;34mBlack passes!\033[0m\n\n";
    printf "Checking code style with pylint...\n";
    pylint compress_pickle;
    printf "\033[1;34mPylint passes!\033[0m\n\n";
fi

pytest -v compress_pickle/tests/ --cov=compress_pickle/ --html=testing-report.html --self-contained-html