# encoding: utf-8
# Copyright (C) 2013 John Törnblom
#
# This file is part of LLVM-P86.
#
# LLVM-P86 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LLVM-P86 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LLVM-P86.  If not, see <http://www.gnu.org/licenses/>.

'''
Tokens and lexer for Pascal-86.

Initially generated with yply from:
  http://ply.googlecode.com/svn/trunk/example/yply

Lexer rules originally taken from:
  http://www.moorecad.com/standardpascal/pascal.l
'''

import sys
import os

from ply import lex

from . import log

QUOTE = r'(\'|")'

tokens = ('AND',
           'ARRAY',
           'ASSIGNMENT',
           'BINDIGSEQ',
           'CASE',
           'CHAR',
           'COLON',
           'COMMA',
           'COMMENT',
           'CONST',
           'DIGSEQ',
           'DIV',
           'DO',
           'DOT',
           'DOTDOT',
           'DOWNTO',
           'ELSE',
           'END',
           'EQUAL',
           'EXTERNAL',
           'FOR',
           'FORWARD',
           'FUNCTION',
           'GE',
           'GOTO',
           'GT',
           'HEXDIGSEQ',
           'IDENTIFIER',
           'IF',
           'IN',
           'INHERIT',
           'LABEL',
           'LBRAC',
           'LE',
           'LPAREN',
           'LT',
           'MINUS',
           'MOD',
           'MODULE',
           'NIL',
           'NOT',
           'NOTEQUAL',
           'OCTDIGSEQ',
           'OF',
           'OR',
           'OTHERWISE',
           'PACKED',
           'PBEGIN',
           'PEXTERN',
           'PFILE',
           'PLUS',
           'PRIVATE',
           'PROCEDURE',
           'PROGRAM',
           'PUBLIC',
           'RBRAC',
           'REALNUMBER',
           'RECORD',
           'REPEAT',
           'RPAREN',
           'SEMICOLON',
           'SET',
           'SLASH',
           'STAR',
           'STARSTAR',
           'STRING',
           'THEN',
           'TO',
           'TYPE',
           'UNTIL',
           'UPARROW',
           'UNPACKED',
           'VAR',
           'VARYING',
           'WHILE',
           'WITH')

reserved_keywords = {
    'and':        'AND',
    'array':      'ARRAY',
    'begin':      'PBEGIN',
    'case':       'CASE',
    'const':      'CONST',
    'div':        'DIV',
    'do':         'DO',
    'downto':     'DOWNTO',
    'else':       'ELSE',
    'end':        'END',
    'extern':     'PEXTERN',
    'file':       'PFILE',
    'for':        'FOR',
    'forward':    'FORWARD',
    'function':   'FUNCTION',
    'goto':       'GOTO',
    'if':         'IF',
    'in':         'IN',
    'inherit':    'INHERIT',
    'label':      'LABEL',
    'mod':        'MOD',
    'module':     'MODULE',
    'nil':        'NIL',
    'not':        'NOT',
    'of':         'OF',
    'or':         'OR',
    'otherwise':  'OTHERWISE',
    'packed':     'PACKED',
    'private':    'PRIVATE',
    'procedure':  'PROCEDURE',
    'program':    'PROGRAM',
    'public':     'PUBLIC',
    'record':     'RECORD',
    'repeat':     'REPEAT',
    'set':        'SET',
    'then':       'THEN',
    'to':         'TO',
    'type':       'TYPE',
    'until':      'UNTIL',
    'var':        'VAR',
    'varying':    'VARYING',
    'while':      'WHILE',
    'with':       'WITH'
}

# A string containing ignored characters (spaces and tabs).
t_ignore = ' \t\r\x0c'


def t_IDENTIFIER(t):
    r"[a-zA-Z]([a-zA-Z0-9_])*"
    if t.value.lower() in reserved_keywords:
        t.type = reserved_keywords[t.value.lower()]

    t.endlexpos = t.lexpos + len(t.value)

    return t


def t_CHAR(t):
    r"(\'([^\\\'])\')|(\"([^\\\"])\")"
    t.value = t.value[1:-1]
    t.endlexpos = t.lexpos + len(t.value)

    return t


def t_STRING(t):
    # r"(\"([^\\\"]|(\\.))*\")|(\'([^\\\']|(\\.))*\')"
    r"(\"([^\\\"]|(\\.))*\")|('([^']|'')*')"

    escaped = 0
    s = t.value[1:-1]
    new_str = ""
    for i in range(0, len(s)):
        c = s[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c

    t.endlexpos = t.lexpos + len(t.value)
    t.value = new_str

    return t


def t_COMMENT(t):
    r"(?s)(\(\*.*?\*\))|({[^}]*})"
    t.lexer.lineno += (t.value.count("\n"))
    t.endlexpos = t.lexpos + len(t.value)


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.endlexpos = t.lexpos + len(t.value)


def t_REALNUMBER(t):
    r"(\d+\.\d+([eE][\+-]\d+)?)|(\d+[eE][\+-]\d+)"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_HEXDIGSEQ(t):
    r'(?i)[0-9][0-9a-f]*H'
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_OCTDIGSEQ(t):
    r'[0-7]+Q'
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_BINDIGSEQ(t):
    r'[01]+B'
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_DIGSEQ(t):
    r"[0-9]+"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_ASSIGNMENT(t):
    r":="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_STARSTAR(t):
    r"\*\*"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_DOTDOT(t):
    r"\.\."
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_GE(t):
    r"\>\="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_NOTEQUAL(t):
    r"\<\>"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LE(t):
    r"\<\="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_COLON(t):
    r":"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_COMMA(t):
    r","
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LBRAC(t):
    r"\["
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_DOT(t):
    r"\."
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_GT(t):
    r"\>"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_EQUAL(t):
    r"\="
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LPAREN(t):
    r"\("
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_LT(t):
    r"\<"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_MINUS(t):
    r"\-"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_PLUS(t):
    r"\+"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_RBRAC(t):
    r"\]"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_RPAREN(t):
    r"\)"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_SEMICOLON(t):
    r";"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_SLASH(t):
    r"/"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_STAR(t):
    r"\*"
    t.endlexpos = t.lexpos + len(t.value)
    return t


def t_UPARROW(t):
    r"\^"
    t.endlexpos = t.lexpos + len(t.value)
    return t


# Error handling rule
def t_error(t):
    log.e("token", "Illegal character '%s'" % t.value[0])


def scanner(debug=False):
    if debug:
        logger = lex.PlyLogger(sys.stderr)
    else:
        logger = lex.NullLogger()

    tab = "llvm_p86._p86_lextab"
    mod = sys.modules[__name__]
    return lex.lex(debuglog=logger,
                   errorlog=logger,
                   optimize=1,
                   lextab=tab,
                   outputdir=os.path.dirname(__file__),
                   module=mod)
