# `compress_pickle`
### Standard python pickle, thinly wrapped with standard compression libraries

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Build Status](https://dev.azure.com/lucianopazneuro/lucianopazneuro/_apis/build/status/lucianopaz.compress_pickle?branchName=master)](https://dev.azure.com/lucianopazneuro/lucianopazneuro/_build/latest?definitionId=1&branchName=master)
[![Coverage Status](https://codecov.io/gh/lucianopaz/compress_pickle/branch/master/graph/badge.svg)](https://codecov.io/gh/lucianopaz/compress_pickle)
[![PyPI](https://img.shields.io/pypi/v/compress_pickle.svg)](https://pypi.org/project/compress-pickle/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

The standard [pickle package](https://docs.python.org/3/library/pickle.html) provides an excellent default tool for serializing arbitrary python objects and storing them to disk. Standard python also includes broad set of [data compression packages](https://docs.python.org/3/library/archiving.html). `compress_pickle` provides an interface to the standard `pickle.dump`, `pickle.load`, `pickle.dumps` and `pickle.loads` functions, but wraps them in order to direct the serialized data through one of the standard compression packages. This way you can seemlessly serialize data to disk or to any file-like object in a compressed way.

`compress_pickle` supports python >= 3.6. If you must support python 3.5, install `compress_pickle==v1.1.1`.

Supported compression protocols:
- [gzip](https://docs.python.org/3/library/gzip.html)
- [bz2](https://docs.python.org/3/library/bz2.html)
- [lzma](https://docs.python.org/3/library/lzma.html)
- [zipfile](https://docs.python.org/3/library/zipfile.html)

Furthermore, `compress_pickle` supports the [`lz4`](https://pypi.org/project/lz4/) compression protocol, that isn't part of the standard python compression packages. This is provided as an optional extra requirement that can be installed as:

```bash
pip install compress_pickle[lz4]
```

Please refer to the [package's documentation](https://lucianopaz.github.io/compress_pickle/html) for more information
