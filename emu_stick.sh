#!/bin/bash
cd `dirname $0`/src
if [ "$1" == -d ]; then
    shift
    gdb --args ../vendor/micropython/unix/micropython $* -O0 -X heapsize=100000 main_stick.py
else
    ../vendor/micropython/unix/micropython $* -O0 -X heapsize=100000 main_stick.py
fi