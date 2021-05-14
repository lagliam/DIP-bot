#!/bin/sh
./python_deps.sh &&
ps -A | grep bot.py | awk '{print $1}' | xargs kill -9 $1