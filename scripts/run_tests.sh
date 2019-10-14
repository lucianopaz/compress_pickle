#!/usr/bin/env bash

set -ex # fail on first error, print commands

if [ ! -z ${TEST_STYLE} ] && [ ${TEST_STYLE} = "True" ]
then
    printf "Checking code style with black...\n";
    black --check compress_pickle;
    printf "\033[1;34mBlack passes!\033[0m\n\n";
    printf "Checking code style with pylint...\n";
    pylint compress_pickle;
    printf "\033[1;34mPylint passes!\033[0m\n\n";
fi

if [ ! -z ${TEST_DOCS} ] && [ ${TEST_DOCS} = "True" ]
then
    sphinx-build -nWT docs/source docs/html;
fi

if [ ! -z ${TEST_UNITTESTS} ] && [ ${TEST_UNITTESTS} = "True" ]
then
    pytest -v compress_pickle/tests/ --cov=compress_pickle/ --cov-report=xml --html=testing-report.html --self-contained-html
fi