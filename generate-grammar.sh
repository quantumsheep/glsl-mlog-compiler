#!/bin/bash

set -e

java -Xmx500M -cp "./bin/antlr-4.9-complete.jar" org.antlr.v4.Tool \
    -Dlanguage=Python3 \
    -no-listener \
    -visitor \
    -o grammar \
    GLSL.g4
