# Generated from GLSL.g4 by ANTLR 4.9
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GLSLParser import GLSLParser
else:
    from GLSLParser import GLSLParser

# This class defines a complete generic visitor for a parse tree produced by GLSLParser.

class GLSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by GLSLParser#translation.
    def visitTranslation(self, ctx:GLSLParser.TranslationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#uniform.
    def visitUniform(self, ctx:GLSLParser.UniformContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#function.
    def visitFunction(self, ctx:GLSLParser.FunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#function_parameter.
    def visitFunction_parameter(self, ctx:GLSLParser.Function_parameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#statement.
    def visitStatement(self, ctx:GLSLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#block_statement.
    def visitBlock_statement(self, ctx:GLSLParser.Block_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#variable_declaration.
    def visitVariable_declaration(self, ctx:GLSLParser.Variable_declarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#expression.
    def visitExpression(self, ctx:GLSLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#literal.
    def visitLiteral(self, ctx:GLSLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#function_call.
    def visitFunction_call(self, ctx:GLSLParser.Function_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#if_statement.
    def visitIf_statement(self, ctx:GLSLParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#while_statement.
    def visitWhile_statement(self, ctx:GLSLParser.While_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#function_return.
    def visitFunction_return(self, ctx:GLSLParser.Function_returnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#encapsulated_expression.
    def visitEncapsulated_expression(self, ctx:GLSLParser.Encapsulated_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GLSLParser#variable_type.
    def visitVariable_type(self, ctx:GLSLParser.Variable_typeContext):
        return self.visitChildren(ctx)



del GLSLParser