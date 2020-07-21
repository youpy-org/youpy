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
import subprocess
import errno
from contextlib import contextmanager

from setuptools import setup
from setuptools import find_packages
from setuptools.command.sdist import sdist

from wheel.bdist_wheel import bdist_wheel

ROOT_DIR = os.path.dirname(__file__)
VERSION_TXT = os.path.join(ROOT_DIR, "VERSION.txt")
REVISION_TXT = os.path.join(ROOT_DIR, "REVISION.txt")
VERSION_SCRIPT = os.path.join(ROOT_DIR, "script", "version")

def readfile(*rnames):
    with codecs.open(os.path.join(ROOT_DIR, *rnames),
                     mode="r",
                     encoding="utf-8") as stream:
        return stream.read()

def writefile(filepath, content):
    with codecs.open(filepath, mode="w", encoding="utf-8") as stream:
        stream.write(content)

def read_requirements():
    requirements = []
    with open(os.path.join(ROOT_DIR, "requirements.txt")) as stream:
        for line in stream:
            line = line.strip()
            if line.startswith("#"):
                continue
            requirements.append(line)
    return requirements

def get_version():
    try:
        return readfile(VERSION_TXT).strip()
    except IOError as e:
        if e.errno == errno.ENOENT:
            cmd = [VERSION_SCRIPT, "get", "--no-dirty"]
            return subprocess.check_output(cmd).decode().strip()

def get_revision():
    try:
        return readfile(REVISION_TXT).strip()
    except IOError as e:
        if e.errno == errno.ENOENT:
            cmd = [VERSION_SCRIPT, "revision"]
            return subprocess.check_output(cmd).decode().strip()

def is_git_dir(dirpath=None):
    if dirpath is None:
        dirpath = os.getcwd()
    cmd = ["git", "-C", str(dirpath), "rev-parse", "--git-dir"]
    try:
        with open(os.devnull, "wb") as devnull:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
    except subprocess.CalledProcessError:
        return False
    return True

def git_file_is_modified(filepath):
    cmd = ["git", "status", "--porcelain", str(filepath)]
    output = subprocess.check_output(cmd).decode()
    return output != u''

def sed_i(script, *filepaths):
    cmd = [ "sed", "-i", '', "-e", script ] + list(filepaths)
    subprocess.check_call(cmd)

def rm_f(path, verbose=False):
    if verbose:
        print("remove %s"%(path,))
    try:
        os.unlink(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise e

@contextmanager
def inject_version_info():
    youpy_main_py = "youpy/__main__.py"
    if not is_git_dir():
        yield
        return
    if git_file_is_modified(youpy_main_py):
        raise RuntimeError("'%s' has un-commited changes"%(youpy_main_py,))
    try:
        print("inject version number into module")
        VERSION = get_version()
        sed_i(
            "s/^__version__ = 'dev'$/__version__ = '%s'/"%(VERSION,),
            youpy_main_py)
        writefile(VERSION_TXT, VERSION)
        print("inject revision number into module")
        REVISION = get_revision()
        writefile(REVISION_TXT, REVISION)
        sed_i(
            "s/^__revision__ = 'git'$/__revision__ = '%s'/"%(REVISION,),
            youpy_main_py)
        yield
    finally:
        print("restore %s"%(youpy_main_py,))
        subprocess.check_call(["git", "checkout", youpy_main_py])
        rm_f(VERSION_TXT, verbose=True)
        rm_f(REVISION_TXT, verbose=True)

class SDistProxy(sdist):
    """Hook sdist command"""

    def run(self):
        with inject_version_info():
            # Super class is an old-style class, so we use old-style
            # "super" call.
            sdist.run(self)

class BDistWheelProxy(bdist_wheel):

    def run(self):
        with inject_version_info():
            # Super class is an old-style class, so we use old-style
            # "super" call.
            bdist_wheel.run(self)

setup(

    # ===================
    # Project description
    # ===================

    name="youpy",
    author="Nicolas Despres",
    #author_email="TODO: email of googlegroup?",
    version=get_version(),
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
    cmdclass={
        'sdist': SDistProxy,
        'bdist_wheel': BDistWheelProxy,
    },
)
