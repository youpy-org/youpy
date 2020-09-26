Introduction
===============

Detail basic command to know when hacking `youpy`.
All commands must be executed from the root of the repository.

Prefer to use GNU Make 4.x.

# Development tool chain

```bash
python -m pip install -r requirements.txt
```

# Test suite

Use this command to run the entire test suite:

```bash
python -m unittest discover -s youpy.test.unit
```

# Release

1. Set the version of python you want to test
   ```bash
   export PYENV_VERSION=x.y.z
   ```
1. Look at the previous released version
   ```bash
   git describe
   ```
1. Choose a version number and store it in the `V` bash variable.
1. Write release note to `doc/RelNotes/$V.txt`.
   You can
   have a look at the new patches included in this release using this command:
   ```bash
   git log $(git describe --always --match 'v*' --abbrev=0)..master
   ```
1. Commit the release notes.
1. Write the VERSION file:
   ```bash
   echo $V > VERSION
   ```
1. Make a distribution
   ```bash
   make dist
   ```
1. Test the distribution
   ```bash
   make test-dist
   ```
1. Publish on the *test* server
   ```bash
   make publish-test
   ```
1. Publish on the *real* server
   ```bash
   make publish
   ```
1. Unset your variables.
   ```bash
   unset V PYENV_VERSION
   ```
1. Remove version file.
   ```bash
   make clean-version
   ```
