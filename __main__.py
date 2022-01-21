import os
import sys

from antlr4 import *

from grammar.GLSLLexer import GLSLLexer
from grammar.GLSLParser import GLSLParser
from visitor import GLSLVisitor


def readfile(path: str):
    with open(path, 'r') as f:
        return f.read()


if __name__ == '__main__':
    internal = readfile(f'{os.path.dirname(os.path.abspath(__file__))}/internal.glsl')
    sources = readfile(sys.argv[1])

    input_stream = InputStream(f'{internal}\n\n{sources}')
    lexer = GLSLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = GLSLParser(stream)
    visitor = GLSLVisitor()

    tree = parser.translation()
    output = visitor.visitTranslation(tree)

    print('\n'.join(output.instructions))
