import itertools
from typing import Dict, List, Optional, TypeVar

from antlr4 import *

from grammar.GLSLParser import GLSLParser


class Instructions:
    def __init__(self, instructions: List[str] = [], value: Optional[str] = None):
        self.instructions = instructions.copy()
        self.value = value

    def add_instructions(self, *instructions_list: List[str]):
        for instructions in instructions_list:
            self.instructions += instructions

        return self

    def merge_instructions(self, *others: 'Instructions'):
        for other in others:
            self.add_instructions(other.instructions)
            self.set_instructions_value(other.value)

        return self

    def set_instructions_value(self, value: Optional[str]):
        self.value = value
        return self

    def add_left_padding(self, skip: int = 0):
        self.instructions[skip:] = map(lambda instruction: f'  {instruction}', self.instructions[skip:])
        return self


class GLSLVariable(Instructions):
    def __init__(self, value: str, type: str = None):
        super().__init__([], value)
        self.type = type

    def set_variable_type(self, type: str):
        self.type = type
        return self


class GLSLFunction(GLSLVariable):
    def __init__(self, name: str, return_type: str, parameters: List[GLSLVariable] = []):
        super().__init__(name, None)
        self.return_type = return_type
        self.parameters = parameters
        self.used_functions: List['GLSLFunction'] = []

    def add_used_function(self, function: 'GLSLFunction'):
        self.used_functions.append(function)
        return self


class Scope:
    def __init__(self, prefix: str = '', parent: 'Scope' = None):
        self.prefix = prefix
        self.parent = parent

        self.values: Dict[str, List[GLSLVariable]] = {}
        self.predefined_values: Dict[str, List[GLSLVariable]] = {}
        self.current_function: GLSLFunction = None

    def default():
        scope = Scope()
        scope.predefined_values = {
            'gl_FragColor': [GLSLVariable('gl_FragColor', 'vec4')],
            'gl_FragCoord': [GLSLVariable('gl_FragCoord', 'vec2')],

            'u_resolution': [GLSLVariable('u_resolution', 'vec2')],
            'u_time': [GLSLVariable('u_time', 'float')],

            'min': [
                GLSLFunction('min', 'float', [GLSLVariable('__f_args_0', 'float'), GLSLVariable('__f_args_1', 'float')]).add_instructions([
                    f'min:',
                    f'    op min __f_return_value __f_args_0 __f_args_1',
                    f'    set @counter __f_min_callback',
                ]),
            ],
            'max': [
                GLSLFunction('max', 'float', [GLSLVariable('__f_args_0', 'float'), GLSLVariable('__f_args_1', 'float')]).add_instructions([
                    f'max:',
                    f'    op max __f_return_value __f_args_0 __f_args_1',
                    f'    set @counter __f_max_callback',
                ]),
            ],
            'abs': [
                GLSLFunction('abs', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'abs:',
                    f'    op abs __f_return_value __f_args_0',
                    f'    set @counter __f_abs_callback',
                ]),
            ],

            'length': [
                GLSLFunction('length', 'float', [GLSLVariable('__f_args_0', 'vec2')]).add_instructions([
                    f'length:',
                    f'    op len __f_return_value __f_args_0.x __f_args_0.y',
                    f'    set @counter __f_length_callback',
                ]),
            ],
            'sqrt': [
                GLSLFunction('sqrt', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'sqrt:',
                    f'    op sqrt __f_return_value __f_args_0',
                    f'    set @counter __f_sqrt_callback',
                ]),
            ],

            'sin': [
                GLSLFunction('sin', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'sin:',
                    f'    op sin __f_return_value __f_args_0',
                    f'    op mul __f_return_value __f_return_value 57.2958',
                    f'    set @counter __f_sin_callback',
                ]),
            ],
            'cos': [
                GLSLFunction('cos', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'cos:',
                    f'    op cos __f_return_value __f_args_0',
                    f'    set @counter __f_cos_callback',
                ]),
            ],
            'tan': [
                GLSLFunction('tan', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'tan:',
                    f'    op tan __f_return_value __f_args_0',
                    f'    set @counter __f_tan_callback',
                ]),
            ],

            'asin': [
                GLSLFunction('asin', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'asin:',
                    f'    op asin __f_return_value __f_args_0',
                    f'    set @counter __f_asin_callback',
                ]),
            ],
            'acos': [
                GLSLFunction('acos', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'acos:',
                    f'    op acos __f_return_value __f_args_0',
                    f'    set @counter __f_acos_callback',
                ]),
            ],
            'atan': [
                GLSLFunction('atan', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'atan:',
                    f'    op atan __f_return_value __f_args_0',
                    f'    set @counter __f_atan_callback',
                ]),
            ],

            'floor': [
                GLSLFunction('floor', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'floor:',
                    f'    op floor __f_return_value __f_args_0',
                    f'    set @counter __f_floor_callback',
                ]),
            ],
            'ceil': [
                GLSLFunction('ceil', 'float', [GLSLVariable('__f_args_0', 'float')]).add_instructions([
                    f'ceil:',
                    f'    op ceil __f_return_value __f_args_0',
                    f'    set @counter __f_ceil_callback',
                ]),
            ],
        }

        return scope

    def get(self, name: str, args: List[GLSLVariable] = None) -> Optional[GLSLVariable]:
        scoped_name = f'{self.prefix}{name}'

        values = (self.values[scoped_name] if scoped_name in self.values else []) + \
            (self.predefined_values[name] if name in self.predefined_values else [])

        for value in values:
            if args is not None:
                if type(value) is GLSLFunction and len(args) == len(value.parameters):
                    ok = True

                    for i, arg in enumerate(args):
                        arg_type = arg.type
                        parameter_type = value.parameters[i].type

                        if arg_type in ['float', 'int', 'uint', 'bool']:
                            if parameter_type not in ['float', 'int', 'uint', 'bool']:
                                ok = False
                                break
                        elif arg_type in ['vec2', 'vec3', 'vec4']:
                            if parameter_type not in ['vec2', 'vec3', 'vec4']:
                                ok = False
                                break

                    if ok:
                        return value
            else:
                return value

        if self.parent is not None:
            return self.parent.get(name, args)

        return None

    def count(self, name: str) -> int:
        scoped_name = f'{self.prefix}{name}'

        values = self.values[scoped_name] if scoped_name in self.values else []
        functions = filter(lambda value: type(value) is GLSLFunction, values)

        predefined_values = self.predefined_values[name] if name in self.predefined_values else []
        predefined_functions = filter(lambda value: type(value) is GLSLFunction, predefined_values)

        return len(list(predefined_functions)) + len(list(functions)) + (self.parent.count(name) if self.parent is not None else 0)

    def add(self, name: str, value: GLSLVariable):
        scoped_name = f'{self.prefix}{name}'

        if scoped_name not in self.values:
            self.values[scoped_name] = []

        self.values[scoped_name].append(value)


def permutations(s: str):
    return list(map(lambda a: ''.join(a), itertools.permutations(s)))


class GLSLVisitor(ParseTreeVisitor):
    scope = Scope.default()

    used_print = False

    def __push_scope(self, prefix: str):
        parent = self.scope

        self.scope = Scope(f'__var_{prefix}_', parent)
        self.scope.current_function = parent.current_function

    def __pop_scope(self):
        self.scope = self.scope.parent

    variable_counter = 0

    def __last_counter(self):
        return max(0, self.variable_counter - 1)

    def __inc_counter(self):
        current = self.variable_counter
        self.variable_counter += 1
        return current

    # Visit a parse tree produced by GLSLParser#translation_unit.
    def visitTranslation(self, ctx: GLSLParser.TranslationContext) -> Instructions:
        functions = [self.visitFunction(function_context) for function_context in ctx.function()]

        used_functions: List[GLSLFunction] = []
        functions_to_add: List[GLSLFunction] = []

        for function in functions:
            if function.value == 'main':
                used_functions.append(function)
                functions_to_add.extend(function.used_functions)
                break

        while len(functions_to_add) > 0:
            function = functions_to_add.pop()

            if function not in used_functions:
                used_functions.append(function)
                functions_to_add.extend(function.used_functions)

        return Instructions()\
            .add_instructions([
                f'set __displaySize 80',
                f'set __displayName display1',

                f'set gl_FragColor.x 0',
                f'set gl_FragColor.y 0',
                f'set gl_FragColor.z 0',
                f'set gl_FragColor.w 0',

                f'set u_resolution.x __displaySize',
                f'set u_resolution.y __displaySize',
                f'set u_time @time',

                f'set __y 0',
                f'__loopY:',
                f'    set __x 0',
                f'    __loopX:',
                f'        op add gl_FragCoord.x __x 0.5',
                f'        op add gl_FragCoord.y __y 0.5',

                f'        op add __f_main_callback @counter 1',
                f'        jump main always',

                f'        printflush message1' if self.used_print else '',

                f'        op add __f___internal_set_pixel_callback @counter 1',
                f'        jump __internal_set_pixel always',

                f'        op add __x __x 1',
                f'        jump __loopX lessThan __x __displaySize',
                f'    op add __y __y 1',
                f'    jump __loopY lessThan __y __displaySize',
                f'_exit:',
                f'end',
            ])\
            .add_instructions([
                f'__internal_set_pixel:',
                f'    op mul rgba.r gl_FragColor.x 255',
                f'    op min rgba.r rgba.r 255',
                f'    op max rgba.r 0 rgba.r',

                f'    op mul rgba.g gl_FragColor.y 255',
                f'    op min rgba.g rgba.g 255',
                f'    op max rgba.g 0 rgba.g',

                f'    op mul rgba.b gl_FragColor.z 255',
                f'    op min rgba.b rgba.b 255',
                f'    op max rgba.b 0 rgba.b',

                f'    op mul rgba.a gl_FragColor.w 255',
                f'    op min rgba.a rgba.a 255',
                f'    op max rgba.a 0 rgba.a',
                f'    draw color rgba.r rgba.g rgba.b rgba.a 0 0',
                f'    draw rect __x __y 1 1 0 0',
                f'    drawflush __displayName',
                f'    set @counter __f___internal_set_pixel_callback',
            ])\
            .merge_instructions(*used_functions)

    # Visit a parse tree produced by GLSLParser#uniform.
    def visitUniform(self, ctx: GLSLParser.UniformContext):
        raise Exception("Not implemented")

    # Visit a parse tree produced by GLSLParser#function.
    def visitFunction(self, ctx: GLSLParser.FunctionContext) -> GLSLFunction:
        function_name = ctx.IDENTIFIER().getText()
        same_functions_count = self.scope.count(function_name)

        function_name_overload = function_name
        if same_functions_count > 0:
            function_name_overload = f'{function_name}__{same_functions_count}'

        function_return_type = self.visitVariable_type(ctx.variable_type())

        function_parameters: List[GLSLVariable] = []
        for parameter_context in ctx.function_parameter():
            function_parameters.append(self.visitFunction_parameter(parameter_context))

        function = GLSLFunction(function_name_overload, function_return_type, function_parameters)

        self.scope.add(function_name, function)
        function.add_instructions([f'{function.value}:'])
        self.__push_scope(function_name_overload)
        self.scope.current_function = function

        for i in range(len(function_parameters)):
            function_parameter = function_parameters[i]
            name = function_parameter.value
            scoped_name = f'{self.scope.prefix}{name}'

            function_parameter.set_instructions_value(scoped_name)

            if function_parameter.type in ['vec2', 'vec3', 'vec4']:
                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }
                properties = ['x', 'y', 'z', 'w'][:vec_size[function_parameter.type]]

                for property in properties:
                    function.add_instructions([f'set {scoped_name}.{property} __f_args_{i}.{property}'])
            else:
                function.add_instructions([f'set {scoped_name} __f_args_{i}'])

            self.scope.add(name, function_parameter)

        if block_statement_context := ctx.block_statement():
            statements = self.visitBlock_statement(block_statement_context, False)
            function.add_instructions(statements.instructions)

        self.__pop_scope()
        function.add_instructions([f'set @counter __f_{function.value}_callback'])

        return function.add_left_padding(skip=1)

    # Visit a parse tree produced by GLSLParser#function_parameter.

    def visitFunction_parameter(self, ctx: GLSLParser.Function_parameterContext) -> GLSLVariable:
        parameter_name = ctx.IDENTIFIER().getText()
        parameter_type = self.visitVariable_type(ctx.variable_type())

        return GLSLVariable(parameter_name, parameter_type)

    # Visit a parse tree produced by GLSLParser#statement.
    def visitStatement(self, ctx: GLSLParser.StatementContext) -> Instructions:
        if block_statement_context := ctx.block_statement():
            return self.visitBlock_statement(block_statement_context)
        elif variable_declaration_context := ctx.variable_declaration():
            return self.visitVariable_declaration(variable_declaration_context)
        elif expression_context := ctx.expression():
            return self.visitExpression(expression_context)
        elif function_return_context := ctx.function_return():
            return self.visitFunction_return(function_return_context)
        elif if_statement_context := ctx.if_statement():
            return self.visitIf_statement(if_statement_context)

        raise Exception("Not implemented")

    # Visit a parse tree produced by GLSLParser#block_statement.
    def visitBlock_statement(self, ctx: GLSLParser.Block_statementContext, new_scope: bool = True) -> Instructions:
        instructions = Instructions()

        if new_scope:
            self.__push_scope(f'{self.__inc_counter()}')

        for statement_context in ctx.statement():
            statement = self.visitStatement(statement_context)
            instructions.add_instructions(statement.instructions)

        if new_scope:
            self.__pop_scope()

        return instructions

    # Visit a parse tree produced by GLSLParser#variable_declaration.
    def visitVariable_declaration(self, ctx: GLSLParser.Variable_declarationContext) -> Instructions:
        variable_type = self.visitVariable_type(ctx.variable_type())
        variable_name = ctx.IDENTIFIER().getText()

        instructions = Instructions()

        expression: GLSLVariable = None

        if expression_context := ctx.expression():
            expression = self.visitExpression(expression_context)
            instructions.merge_instructions(expression)

        scoped_name = f'{self.scope.prefix}{variable_name}'
        variable = GLSLVariable(scoped_name, variable_type)
        self.scope.add(variable_name, variable)

        if expression is None:
            return instructions.add_instructions([f'set {scoped_name} 0'])

        if variable.type in ['vec2', 'vec3', 'vec4']:
            vec_size = {
                'vec2': 2,
                'vec3': 3,
                'vec4': 4,
            }
            properties = ['x', 'y', 'z', 'w'][:vec_size[variable.type]]

            for property in properties:
                instructions.add_instructions([f'set {scoped_name}.{property} {expression.value}.{property}'])

            return instructions

        return instructions.add_instructions([f'set {scoped_name} {expression.value}'])

    # Visit a parse tree produced by GLSLParser#expression.
    def visitExpression(self, ctx: GLSLParser.ExpressionContext) -> GLSLVariable:
        if ctx.DOT() is not None:
            expression = self.visitExpression(ctx.expression(0))
            identifier: str = ctx.IDENTIFIER().getText()

            properties = ['x', 'y', 'z', 'w']

            if expression.type in ['vec2', 'vec3', 'vec4']:
                temp_variable = None

                if identifier in permutations('xy'):
                    temp_variable = GLSLVariable(f'__{self.__inc_counter()}', 'vec2')
                elif identifier in permutations('xyz'):
                    temp_variable = GLSLVariable(f'__{self.__inc_counter()}', 'vec3')
                elif identifier in permutations('xyzw'):
                    temp_variable = GLSLVariable(f'__{self.__inc_counter()}', 'vec4')

                if temp_variable is not None:
                    for property in identifier:
                        temp_variable\
                            .add_instructions(expression.instructions)\
                            .add_instructions([
                                f'set {temp_variable.value}.{properties.pop(0)} {expression.value}.{property}'
                            ])

                    return temp_variable

                return GLSLVariable(f'{expression.value}.{identifier}', 'float')\
                    .add_instructions(expression.instructions)

            raise Exception(f"Not implemented")

        if literal_context := ctx.literal():
            return self.visitLiteral(literal_context)

        if function_call_context := ctx.function_call():
            return self.visitFunction_call(function_call_context)

        if encapsulated_expression_context := ctx.encapsulated_expression():
            return self.visitEncapsulated_expression(encapsulated_expression_context)

        if identifier_context := ctx.IDENTIFIER():
            variable = self.scope.get(identifier_context.getText())

            if variable is None:
                raise Exception(f"Variable '{identifier_context.getText()}' not found")

            return variable

        if ctx.OPERATOR_SUB() is not None and len(ctx.expression()) == 1:
            expression = self.visitExpression(ctx.expression(0))

            variable = GLSLVariable(f'__{self.__inc_counter()}', expression.type)\
                .add_instructions(expression.instructions)

            return variable\
                .add_instructions([f'op sub {variable.value} 0 {expression.value}'])

        expression_left = self.visitExpression(ctx.expression(0))
        expression_right = self.visitExpression(ctx.expression(1))

        variable = GLSLVariable(f'__{self.__inc_counter()}', expression_left.type)\
            .add_instructions(expression_left.instructions)\
            .add_instructions(expression_right.instructions)

        if ctx.OPERATOR_ASSIGN() is not None:
            if expression_right.type in ['vec2', 'vec3', 'vec4']:
                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }
                properties = ['x', 'y', 'z', 'w'][:vec_size[expression_left.type]]

                for property in properties:
                    variable.add_instructions(
                        [f'set {expression_left.value}.{property} {expression_right.value}.{property}'])

            return variable.add_instructions([f'set {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_MUL() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4']:
                if expression_right.type in ['vec2', 'vec3', 'vec4']:
                    raise Exception(
                        f'Multiplying a {expression_left.type} by a {expression_right.type} is not implemented')

                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }
                properties = ['x', 'y', 'z', 'w'][:vec_size[expression_left.type]]

                for property in properties:
                    variable.add_instructions(
                        [f'op mul {variable.value}.{property} {expression_left.value}.{property} {expression_right.value}'])

                return variable

            return variable.add_instructions([f'op mul {variable.value} {expression_left.value} {expression_right.value}'])
        if ctx.OPERATOR_DIV() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4']:
                if expression_left.type != expression_right.type:
                    raise Exception(
                        f'Dividing a {expression_left.type} by a {expression_right.type} is not implemented')

                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }
                properties = ['x', 'y', 'z', 'w'][:vec_size[expression_left.type]]

                for property in properties:
                    variable.add_instructions(
                        [f'op div {variable.value}.{property} {expression_left.value}.{property} {expression_right.value}.{property}'])

                return variable

            return variable.add_instructions([f'op div {variable.value} {expression_left.value} {expression_right.value}'])
        if ctx.OPERATOR_MOD() is not None:
            return variable.add_instructions([f'op mod {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_ADD() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4']:
                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }
                properties = ['x', 'y', 'z', 'w'][:vec_size[expression_left.type]]

                if expression_right.type in ['vec2', 'vec3', 'vec4']:
                    if expression_left.type != expression_right.type:
                        raise Exception(
                            f'Adding a {expression_left.type} by a {expression_right.type} is not implemented')

                    for property in properties:
                        variable.add_instructions(
                            [f'op add {variable.value}.{property} {expression_left.value}.{property} {expression_right.value}.{property}'])
                else:
                    for property in properties:
                        variable.add_instructions(
                            [f'op add {variable.value}.{property} {expression_left.value}.{property} {expression_right.value}'])

                return variable

            return variable.add_instructions([f'op add {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_SUB() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4']:
                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }
                properties = ['x', 'y', 'z', 'w'][:vec_size[expression_left.type]]

                if expression_right.type in ['vec2', 'vec3', 'vec4']:
                    if expression_left.type != expression_right.type:
                        raise Exception(
                            f'Substracting a {expression_left.type} by a {expression_right.type} is not implemented')

                    for property in properties:
                        variable.add_instructions(
                            [f'op sub {variable.value}.{property} {expression_left.value}.{property} {expression_right.value}.{property}'])
                else:
                    for property in properties:
                        variable.add_instructions(
                            [f'op sub {variable.value}.{property} {expression_left.value}.{property} {expression_right.value}'])

                return variable

            return variable.add_instructions([f'op sub {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_EQ() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4'] or expression_right.type in ['vec2', 'vec3', 'vec4']:
                raise Exception(f'Equal operator is not implemented for vectors')

            return variable.add_instructions([f'op equal {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_NE() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4'] or expression_right.type in ['vec2', 'vec3', 'vec4']:
                raise Exception(f'Not Equal operator is not implemented for vectors')

            return variable.add_instructions([f'op notEqual {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_LT() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4'] or expression_right.type in ['vec2', 'vec3', 'vec4']:
                raise Exception(f'Less Than operator is not implemented for vectors')

            return variable.add_instructions([f'op lessThan {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_GT() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4'] or expression_right.type in ['vec2', 'vec3', 'vec4']:
                raise Exception(f'Greater Than operator is not implemented for vectors')

            return variable.add_instructions([f'op greaterThan {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_LE() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4'] or expression_right.type in ['vec2', 'vec3', 'vec4']:
                raise Exception(f'Less Than operator is not implemented for vectors')

            return variable.add_instructions([f'op lessThanEq {variable.value} {expression_left.value} {expression_right.value}'])
        elif ctx.OPERATOR_GE() is not None:
            if expression_left.type in ['vec2', 'vec3', 'vec4'] or expression_right.type in ['vec2', 'vec3', 'vec4']:
                raise Exception(f'Greater Than operator is not implemented for vectors')

            return variable.add_instructions([f'op greaterThanEq {variable.value} {expression_left.value} {expression_right.value}'])
        else:
            raise Exception("Not implemented")

    # Visit a parse tree produced by GLSLParser#literal.
    def visitLiteral(self, ctx: GLSLParser.LiteralContext) -> GLSLVariable:
        if float_context := ctx.FLOAT():
            value = float_context.getText()

            if value.endswith('f'):
                value = value[:-1]

            return GLSLVariable(value, 'float')
        elif integer_context := ctx.INTEGER():
            return GLSLVariable(integer_context.getText(), 'int')
        elif octal_context := ctx.OCTAL():
            value = octal_context.getText()
            return GLSLVariable(str(int(value, 8)), 'int')
        elif hex_context := ctx.HEX():
            value = hex_context.getText()
            return GLSLVariable(str(int(value, 16)), 'int')
        elif true_context := ctx.TRUE():
            return GLSLVariable(true_context.getText(), 'bool')
        elif false_context := ctx.FALSE():
            return GLSLVariable(false_context.getText(), 'bool')

    # Visit a parse tree produced by GLSLParser#function_call.
    def visitFunction_call(self, ctx: GLSLParser.Function_callContext) -> Instructions:
        instructions = Instructions()
        args: List[GLSLVariable] = []

        for expression_context in ctx.expression():
            expression = self.visitExpression(expression_context)
            instructions.add_instructions(expression.instructions)

            if expression.value == '__f_return_value':
                arg = GLSLVariable(f'__{self.__inc_counter()}', expression.type)

                if expression.type in ['vec2', 'vec3', 'vec4']:
                    vec_size = {
                        'vec2': 2,
                        'vec3': 3,
                        'vec4': 4,
                    }
                    properties = ['x', 'y', 'z', 'w'][:vec_size[expression.type]]

                    for property in properties:
                        instructions.add_instructions(
                            [f'set {arg.value}.{property} {expression.value}.{property}'])
                else:
                    instructions.add_instructions([f'set {arg.value} {expression.value}'])

                args.append(arg)
            else:
                args.append(expression)

        if ctx.PRINT() is not None:
            self.used_print = True

            for i in range(len(args)):
                if i > 0:
                    instructions.add_instructions(['print " "'])

                arg = args[i]

                if arg.type in ['vec2', 'vec3', 'vec4']:
                    vec_size = {
                        'vec2': 2,
                        'vec3': 3,
                        'vec4': 4,
                    }
                    properties = ['x', 'y', 'z', 'w'][:vec_size[arg.type]]

                    instructions.add_instructions(['print "("'])

                    for j in range(len(properties)):
                        if j > 0:
                            instructions.add_instructions(['print ", "'])

                        instructions.add_instructions([f'print {arg.value}.{properties[j]}'])

                    instructions.add_instructions(['print ")"'])
                else:
                    instructions.add_instructions([
                        f'print {arg.value}',
                    ])

            return instructions

        if ctx.TYPE_VEC2() is not None or ctx.TYPE_VEC3() is not None or ctx.TYPE_VEC4() is not None:
            if ctx.TYPE_VEC2() is not None:
                if len(args) > 2:
                    raise Exception("Invalid number of arguments for vec2")

                variable_type = 'vec2'
            elif ctx.TYPE_VEC3() is not None:
                if len(args) > 3:
                    raise Exception("Invalid number of arguments for vec3")

                variable_type = 'vec3'
            elif ctx.TYPE_VEC4() is not None:
                if len(args) > 4:
                    raise Exception("Invalid number of arguments for vec4")

                variable_type = 'vec4'

            variable = GLSLVariable(f'__{self.__inc_counter()}', variable_type)\
                .add_instructions(instructions.instructions)
            properties = ['x', 'y', 'z', 'w']

            if len(args) == 1 and args[0].type not in ['vec2', 'vec3', 'vec4']:
                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }

                for property in properties[:vec_size[variable.type]]:
                    variable.add_instructions([f'set {variable.value}.{property} {args[0].value}'])
            else:
                for expression in args:
                    if expression.type == 'vec2':
                        variable.add_instructions([
                            f'set {variable.value}.{properties.pop(0)} {expression.value}.x',
                            f'set {variable.value}.{properties.pop(0)} {expression.value}.y',
                        ])
                    elif expression.type == 'vec3':
                        variable.add_instructions([
                            f'set {variable.value}.{properties.pop(0)} {expression.value}.x',
                            f'set {variable.value}.{properties.pop(0)} {expression.value}.y',
                            f'set {variable.value}.{properties.pop(0)} {expression.value}.z',
                        ])
                    else:
                        variable.add_instructions([
                            f'set {variable.value}.{properties.pop(0)} {expression.value}',
                        ])

            self.scope.add(variable.value, variable)
            return variable

        function_name = ctx.IDENTIFIER().getText()
        function = self.scope.get(function_name, args)

        if function is None:
            raise Exception(f'Function {function_name} not found')

        if type(function) is not GLSLFunction:
            raise Exception(f'{function_name} is not a function')

        self.scope.current_function.add_used_function(function)

        variable = GLSLVariable(f'__f_return_value', function.return_type)\
            .add_instructions(instructions.instructions)

        for i in range(len(args)):
            arg = args[i]

            if arg.type in ['vec2', 'vec3', 'vec4']:
                if function.parameters[i].type != arg.type:
                    raise Exception(f'Passing a {function.parameters[i].type} as a {arg.type} is not implemented')

                vec_size = {
                    'vec2': 2,
                    'vec3': 3,
                    'vec4': 4,
                }
                properties = ['x', 'y', 'z', 'w'][:vec_size[arg.type]]

                for property in properties:
                    variable.add_instructions(
                        [f'set __f_args_{i}.{property} {arg.value}.{property}'])
            else:
                variable.add_instructions([f'set __f_args_{i} {arg.value}'])

        variable.add_instructions([
            f'op add __f_{function.value}_callback @counter 1',
            f'jump {function.value} always',
        ])

        temp_variable = GLSLVariable(f'__{self.__inc_counter()}', variable.type)\
            .add_instructions(variable.instructions)

        if variable.type in ['vec2', 'vec3', 'vec4']:
            vec_size = {
                'vec2': 2,
                'vec3': 3,
                'vec4': 4,
            }
            properties = ['x', 'y', 'z', 'w'][:vec_size[arg.type]]

            for property in properties:
                temp_variable.add_instructions(
                    [f'set {temp_variable.value}.{property} {variable.value}.{property}'])
        else:
            temp_variable.add_instructions([f'set {temp_variable.value} {variable.value}'])

        return temp_variable

    # Visit a parse tree produced by GLSLParser#if_statement.
    def visitIf_statement(self, ctx: GLSLParser.If_statementContext):
        counter = self.__inc_counter()
        label_if = f'__if_{counter}'
        label_endif = f'__if_{counter}_end'
        label_else = f'__else_{counter}'

        if_instructions = Instructions()
        else_instructions = Instructions()

        if ctx.ELSE() is not None:
            else_instructions.add_instructions([f'{label_else}:'])
            else_statement = self.visitStatement(ctx.statement(1))

            else_instructions\
                .add_instructions(else_statement.instructions)\
                .add_instructions([f'jump {label_endif} always'])\
                .add_left_padding(skip=1)
        else:
            label_else = label_endif

        expression = self.visitExpression(ctx.expression())

        if expression.type == 'bool':
            if_instructions.add_instructions([f'jump {label_else} equal {expression.value} false'])
        else:
            if_instructions.add_instructions([f'jump {label_else} equal {expression.value} 0'])

        if_instructions.add_instructions([f'{label_if}:'])
        if_statement = self.visitStatement(ctx.statement(0))

        if_instructions\
            .add_instructions(if_statement.instructions)\
            .add_instructions([f'jump {label_endif} always'])\
            .add_left_padding(skip=2)

        else_instructions.add_instructions([f'{label_endif}:'])

        return Instructions()\
            .add_instructions(expression.instructions)\
            .add_instructions(if_instructions.instructions)\
            .add_instructions(else_instructions.instructions)

    # Visit a parse tree produced by GLSLParser#function_return.
    def visitFunction_return(self, ctx: GLSLParser.Function_returnContext):
        variable = self.visitExpression(ctx.expression())

        if variable.type in ['vec2', 'vec3', 'vec4']:
            vec_size = {
                'vec2': 2,
                'vec3': 3,
                'vec4': 4,
            }
            properties = ['x', 'y', 'z', 'w'][:vec_size[variable.type]]

            for property in properties:
                variable.add_instructions([f'set __f_return_value.{property} {variable.value}.{property}'])
        else:
            variable.add_instructions([f'set __f_return_value {variable.value}'])

        return variable.set_instructions_value('__f_return_value')\
            .add_instructions([
                f'set @counter __f_{self.scope.current_function.value}_callback',
            ])

    # Visit a parse tree produced by GLSLParser#encapsulated_expression.
    def visitEncapsulated_expression(self, ctx: GLSLParser.Encapsulated_expressionContext):
        return self.visitExpression(ctx.expression())

    # Visit a parse tree produced by GLSLParser#variable_type.
    def visitVariable_type(self, ctx: GLSLParser.Variable_typeContext) -> str:
        return ctx.getText()


del GLSLParser
