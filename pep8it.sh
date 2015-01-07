#!/usr/bin/env bash

find . -name '*.py' -type f | xargs autopep8 --in-place --max-line-length=150

