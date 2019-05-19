# `compress_pickle`
### Standard python pickle, thinly wrapped with standard compression libraries

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Build Status](https://travis-ci.org/lucianopaz/compress_pickle.svg?branch=master)](https://travis-ci.org/lucianopaz/compress_pickle)
[![Coverage Status](https://coveralls.io/repos/github/lucianopaz/compress_pickle/badge.svg?branch=master)](https://coveralls.io/github/lucianopaz/compress_pickle?branch=master)
[![PyPI](https://img.shields.io/pypi/v/compress_pickle.svg)](https://pypi.org/project/compress-pickle/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

The standard [pickle package](https://docs.python.org/3/library/pickle.html) provides an excellent default tool for serializing arbitrary python objects and storing them to disk. Standard python also includes broad set of [data compression packages](https://docs.python.org/3/library/archiving.html). `compress_pickle` provides an interface to the standard `pickle.dump` and `pickle.load` functions, but wraps them in order to direct the serialized data through one of the standard compression packages. This way you can seemlessly serialize data to disk in a compressed way.

`compress_pickle` is built and tested in python >= 3.5

Supported compression protocols:
- [gzip](https://docs.python.org/3/library/gzip.html)
- [bz2](https://docs.python.org/3/library/bz2.html)
- [lzma](https://docs.python.org/3/library/lzma.html)
- [zipfile](https://docs.python.org/3/library/zipfile.html) (Note that python3.6 and higher allows to build a file-like buffer into the zip archive, which allows us to use less memory than in python3.5)

Please refer to the [package's documentation](https://lucianopaz.github.io/compress_pickle/html) for more information
