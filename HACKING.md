Introduction
===============

Detail basic command to know when hacking `youpy`.
All commands must be executed from the root of the repository.

# Test suite

Use this command to run the entire test suite:

```bash
python3 -m unittest discover -s youpy.test
```

# How to make a release

1. Write a tag message containing the release notes. You can get the
   list of new commits since the last release using this command:

   ```bash
   git log $(git describe --always --match 'v*' --abbrev=0)..master
   ```

   Store you tag message in a file called `/tmp/youpy.tagmsg` for
   instance.

1.
