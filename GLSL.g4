grammar GLSL;

translation: uniform* function*;

uniform: UNIFORM IDENTIFIER SEMICOLON;

function:
	variable_type IDENTIFIER '(' (
		function_parameter (',' function_parameter)*
	)? ')' block_statement;

function_parameter: variable_type IDENTIFIER;

statement:
	block_statement
	| if_statement
	| while_statement
	| (
		(variable_declaration | expression | function_return) SEMICOLON
	);

block_statement: '{' statement* '}';

variable_declaration:
	variable_type IDENTIFIER ('=' expression)?;

expression:
	(OPERATOR_SUB) expression
	| expression DOT IDENTIFIER
	| expression (OPERATOR_MUL | OPERATOR_DIV | OPERATOR_MOD) expression
	| expression (OPERATOR_ADD | OPERATOR_SUB) expression
	| expression (
		OPERATOR_LT
		| OPERATOR_GT
		| OPERATOR_LE
		| OPERATOR_GE
	) expression
	| expression (OPERATOR_EQ | OPERATOR_NE) expression
	| literal
	| function_call
	| encapsulated_expression
	| IDENTIFIER
	| expression (
		OPERATOR_ASSIGN
		| OPERATOR_ADD_ASSIGN
		| OPERATOR_SUB_ASSIGN
		| OPERATOR_MUL_ASSIGN
		| OPERATOR_DIV_ASSIGN
		| OPERATOR_MOD_ASSIGN
	) expression;

literal: FLOAT | INTEGER | OCTAL | HEX | TRUE | FALSE;

function_call:
	PRINT '(' (expression (',' expression)*)? ')'
	| TYPE_VEC2 '(' expression (',' expression)? ')'
	| TYPE_VEC3 '(' expression (',' expression (',' expression)?)? ')'
	| TYPE_VEC4 '(' expression (
		',' expression (',' expression (',' expression)?)?
	)? ')'
	| IDENTIFIER '(' (expression (',' expression)*)? ')';

if_statement: IF '(' expression ')' statement (ELSE statement)?;

while_statement: WHILE '(' expression ')' statement;

function_return: RETURN expression;

encapsulated_expression: '(' expression ')';

variable_type:
	TYPE_VOID
	| TYPE_FLOAT
	| TYPE_INT
	| TYPE_UINT
	| TYPE_BOOL
	| TYPE_VEC2
	| TYPE_VEC3
	| TYPE_VEC4
	| TYPE_MAT2X2
	| TYPE_MAT2X3
	| TYPE_MAT2X4
	| TYPE_MAT3X2
	| TYPE_MAT3X3
	| TYPE_MAT3X4
	| TYPE_MAT4X2
	| TYPE_MAT4X3
	| TYPE_MAT4X4;

PRINT: 'print';

COLON: ':';

RETURN: 'return';

UNIFORM: 'uniform';

CONST_TOK: 'const';

TRUE: 'true';
FALSE: 'false';

STRUCT: 'struct';

IF: 'if';
ELSE: 'else';

SWITCH: 'switch';
CASE: 'case';
DEFAULT: 'default';

WHILE: 'while';
DO: 'do';
FOR: 'for';
CONTINUE: 'continue';
BREAK: 'break';

TYPE_VOID: 'void';
TYPE_FLOAT: 'float';
TYPE_INT: 'int';
TYPE_UINT: 'uint';
TYPE_BOOL: 'bool';

TYPE_VEC2: 'vec2';
TYPE_VEC3: 'vec3';
TYPE_VEC4: 'vec4';
TYPE_MAT2X2: 'mat2' | 'mat2x2';
TYPE_MAT2X3: 'mat2x3';
TYPE_MAT2X4: 'mat2x4';
TYPE_MAT3X2: 'mat3x2';
TYPE_MAT3X3: 'mat3' | 'mat3x3';
TYPE_MAT3X4: 'mat3x4';
TYPE_MAT4X2: 'mat4x2';
TYPE_MAT4X3: 'mat4x3';
TYPE_MAT4X4: 'mat4' | 'mat4x4';

LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
SEMICOLON: ';';
LBRACKET: '[';
RBRACKET: ']';
COMMA: ',';

DOT: '.';
OPERATOR_ADD: '+';
OPERATOR_SUB: '-';
OPERATOR_MUL: '*';
OPERATOR_DIV: '/';
OPERATOR_MOD: '%';
OPERATOR_NOT: '!';
OPERATOR_BNOT: '~';
OPERATOR_LT: '<';
OPERATOR_GT: '>';
OPERATOR_BAND: '&';
OPERATOR_BOR: '|';
OPERATOR_BXOR: '^';
OPERATOR_INC: '++';
OPERATOR_DEC: '--';
OPERATOR_LSHIFT: '<<';
OPERATOR_RSHIFT: '>>';

OPERATOR_LE: '<=';
OPERATOR_GE: '>=';
OPERATOR_EQ: '==';
OPERATOR_NE: '!=';
OPERATOR_AND: '&&';
OPERATOR_XOR: '^^';
OPERATOR_OR: '||';

OPERATOR_ASSIGN: '=';
OPERATOR_MUL_ASSIGN: '*=';
OPERATOR_DIV_ASSIGN: '/=';
OPERATOR_MOD_ASSIGN: '%=';
OPERATOR_ADD_ASSIGN: '+=';
OPERATOR_SUB_ASSIGN: '-=';
OPERATOR_LSHIFT_ASSIGN: '<<=';
OPERATOR_RSHIFT_ASSIGN: '>>=';
OPERATOR_AND_ASSIGN: '&=';
OPERATOR_XOR_ASSIGN: '^=';
OPERATOR_OR_ASSIGN: '|=';

IDENTIFIER: ('a' ..'z' | 'A' ..'Z' | '_') (
		DIGIT
		| 'a' ..'z'
		| 'A' ..'Z'
		| '_'
	)*;

FLOAT: ((DIGIT+ ('.' DIGIT*)?) | ('.' DIGIT+)) (
		('e' | 'E') ('+' | '-')? DIGIT*
	)? 'f'?;

INTEGER: '0' | ('1' ..'9' DIGIT*);
OCTAL: '0' '0' ..'7'+;
HEX: '0x' (DIGIT | 'a' ..'f' | 'A' ..'F')+;
DIGIT: '0' .. '9';

COMMENT: ('//' ~('\n' | '\r')* '\r'? '\n' | '/*' (.)*? '*/') -> skip;

WS: [ \t]+ -> skip;
EOL: [\r\n] -> channel(HIDDEN);
