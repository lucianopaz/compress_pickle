import codecs
import re
from os import path

from setuptools import setup, find_packages


PROJECT_ROOT = path.dirname(path.abspath(__file__))
REQUIREMENTS_FILE = path.join(PROJECT_ROOT, "requirements.txt")
README_FILE = path.join(PROJECT_ROOT, "README.md")
VERSION_FILE = path.join(PROJECT_ROOT, "compress_pickle", "__init__.py")

NAME = "compress_pickle"
DESCRIPTION = "Standard pickle, wrapped with standard compression libraries"
AUTHOR = "Luciano Paz"
AUTHOR_EMAIL = "luciano.paz.neuro@gmail.com"
URL = "https://github.com/lucianopaz/compress_pickle"


lz4_requires = ["lz4"]
dill_requires = ["dill"]
cloudpickle_requires = ["cloudpickle"]
extras_require = {
    "lz4": lz4_requires,
    "dill": dill_requires,
    "cloudpickle": cloudpickle_requires,
    "full": lz4_requires + dill_requires + cloudpickle_requires,
}


def get_requirements():
    with codecs.open(REQUIREMENTS_FILE) as buff:
        return buff.read().splitlines()


def get_long_description():
    with codecs.open(README_FILE, "rt") as buff:
        return buff.read()


def get_version():
    lines = open(VERSION_FILE, "rt").readlines()
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in lines:
        mo = re.search(version_regex, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError("Unable to find version in %s." % (VERSION_FILE,))


if __name__ == "__main__":
    setup(
        name=NAME,
        version=get_version(),
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        python_requires=">=3.6",
        packages=find_packages(),
        install_requires=get_requirements(),
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        include_package_data=True,
        extras_require=extras_require,
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
