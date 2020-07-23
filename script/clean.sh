#!/usr/bin/env bash
#
#::BEGIN::
# USAGE
#
#  clean.sh
#
# DESCRIPTION
#
#
#
# Copyright (c) 2020, Nicolas Despres
# Report any problem to <nicolas.despres@gmail.com>
#::END::
#

set -o errexit
set -o nounset

export LC_ALL=C
unset CDPATH

ROOT_DIR=$(git rev-parse --show-toplevel)
find "$ROOT_DIR" \
     \( -type f -name '*.pyc' \) \
     -o \( -type d -name '__pycache__' \) \
     -print0 \
  | xargs -0 rm -rf
