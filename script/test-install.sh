#!/usr/bin/env bash
#
#::BEGIN::
# USAGE
#
#  test-install.sh <version>
#
# DESCRIPTION
#
#  Test release uploaded on the test pypi server
#
# Copyright (c) 2020, Nicolas Despres
#::END::
#

set -o errexit
set -o nounset

export LC_ALL=C
unset CDPATH


# Print the message in the header of this file.
usage()
{
  sed -ne '/^#::BEGIN::/,/^#::END::/p' < "$0" \
    | sed -e '/^#::BEGIN::/d;/^#::END::/d' \
    | sed -e 's/^# //; s/^#//'
}

if [ $# -ne 1 ]
then
  usage
  exit 1
fi
VERSION="$1"

pip3 install -i https://test.pypi.org/simple/ "youpy==$VERSION"
python3 -m youpy.examples.BallBar
