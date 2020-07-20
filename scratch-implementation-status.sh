#!/usr/bin/env bash
#
#::BEGIN::
# USAGE
#
#  scratch-implementation-status.sh
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

NOT_IMPLEMENTED_YET=$(grep -c 'not implemented yet' SCRATCH.md)
TOTAL_FEATURES=$(cat SCRATCH.md | grep '^| ' | grep -v '^| \(Block\|-----\) |' | wc -l)
echo "Total features: $TOTAL_FEATURES"
echo "Features not implemented yet: $NOT_IMPLEMENTED_YET"
RATIO=$(echo "scale=2; $NOT_IMPLEMENTED_YET / $TOTAL_FEATURES" | bc)
echo "Implementation completed: $RATIO"
