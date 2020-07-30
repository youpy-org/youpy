# -*- encoding: utf-8 -*-
# Copyright (c) 2015, Nicolas Despres

# Relevant documentation used when writing this file:
#   https://docs.python.org/3/library/distutils.html
#   http://www.diveinto.org/python3/packaging.html
#   http://www.scotttorborg.com/python-packaging/
# and of course several example projects such as: csvkit, nose or buildout.

import os
import sys
import codecs

from setuptools import setup
from setuptools import find_packages

ROOT_DIR = os.path.dirname(__file__)

def read_requirements():
    requirements = []
    with open(os.path.join(ROOT_DIR, "requirements.txt")) as stream:
        for line in stream:
            line = line.strip()
            if line.startswith("#"):
                continue
            requirements.append(line)
    return requirements


from youpy.version import VERSION

### Configure warnings emitted by 'setup()' we are interested in.
import warnings
# Tell 'setup' to report invalid version number as error.
warnings.simplefilter("error", category=UserWarning)

### Do setup
setup(

    # ===================
    # Project description
    # ===================

    name="youpy",
    author="Nicolas Despres",
    #author_email="TODO: email of googlegroup?",
    version=str(VERSION),
    license="BSD 3-clause",
    # TODO(Nicolas Despres): Change this once we have a website.
    description="Python game engine for beginners",
    long_description="Youpy is a simple game engine framework inspired by Scratch for educational use and beginners student.",
    keywords='game education',
    url='https://github.com/nicolasdespres/youpy',
    project_urls={
        "Source code": "https://github.com/nicolasdespres/youpy",
        "Bug tracker": "https://github.com/nicolasdespres/youpy/issues",
    },

    # =====================
    # Deployment directives
    # =====================

    # We only have a single package to distribute and no individual modules
    packages=find_packages(),
    # No individual modules.
    py_modules=[],
    # Include files mentioned MANIFEST.in in the wheel distribution.
    include_package_data=True,
    platforms=["Windows", "macOS", "Linux"],
    # Read dependencies from requirements.txt
    install_requires=read_requirements(),
    # Generate a command line interface driver.
    entry_points={
        'console_scripts': [
            "youpy=youpy.__main__:sys_main",
        ],
    },
    # How to run the test suite.
    test_suite='youpy/test',
    # Pick some from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Education',
        'Topic :: Multimedia',
    ],
)
