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
Preprocessor for Pascal-86.
'''

import sys
import os

from ply import lex
from ply import yacc

from . import log


tokens = ('WHITESPACE',
          'NEWLINE',
          'DOLLAR',
          'LPAREN',
          'RPAREN',

          'IF',
          'NOT',
          'ELSE',
          'ENDIF',

          'INCLUDE',
          'EJECT',
          'COND',
          'NOCOND',
          'INTERRUPT',

          'ANYTHING',
          'COMMENT',
          'IDENTIFIER')

reserved_keywords = {
    'include'   : 'INCLUDE',
    'if'        : 'IF',
    'not'       : 'NOT',
    'else'      : 'ELSE',
    'endif'     : 'ENDIF',
    'eject'     : 'EJECT',
    'cond'      : 'COND',
    'nocond'    : 'NOCOND',
    'interrupt' : 'INTERRUPT',
}

precedence = (
    ('right', 'DOLLAR'),
    ('right', 'INCLUDE', 'IF', 'ELSE', 'ENDIF', 'EJECT', 'COND', 'NOCOND',
              'INTERRUPT'),
)

pre_includes = ['.']
pre_defines = dict()
pre_filename = []


def t_COMMENT(t):
    r"(?s)(\(\*.*?\*\))|({[^}]*})"
    t.lexer.lineno += (t.value.count("\n"))
    return t


def t_IDENTIFIER(t):
    r"[a-zA-Z]([a-zA-Z0-9_\.:])*"
    if t.value.lower() in reserved_keywords:
        t.type = reserved_keywords[t.value.lower()]
    return t


def t_WHITESPACE(t):
    r"[ \t\x0c\r]"
    t.lexer.lineno += (t.value.count("\n"))
    return t


def t_NEWLINE(t):
    r"\n"
    t.lexer.lineno += (t.value.count("\n"))
    return t


def t_DOLLAR(t):
    r"\$"
    return t


def t_RPAREN(t):
    r"\)"
    return t


def t_LPAREN(t):
    r"\("
    return t


def t_ANYTHING(t):
    r"[^ \t\n\$\(\)]+"
    t.lexer.lineno += (t.value.count("\n"))
    return t


def t_error(t):
    log.e("pre", "Illegal character '%s'" % t.value[0])


def debug(s):
    log.d("pre", "untested rule - %s", s)


def _get_character_stream(filename):
    if filename == '-':
        chars = sys.stdin.read()
    else:
        fd = open(filename, "rb")
        chars = fd.read()
        fd.close()

    # python 3
    if not isinstance(chars, str):
        chars = chars.decode()

    return chars


class TextNode(object):

    def __init__(self, value, pos=None):
        self.pos = pos
        self.value = value
        self.child = None

    @property
    def nodes(self):
        l = [self]

        if self.child:
            l.extend(self.child.nodes)

        return l

    def append(self, y):
        if isinstance(y, DirectiveNode):
            self.nodes[-1].child = y

        elif y.pos[0] == self.pos[0] and not self.child:
            self.value += y.value

        elif self.child:
            self.child.append(y)

        else:
            self.nodes[-1].child = y

    def __str__(self):
        return self.value


class DirectiveNode(object):

    def __init__(self, value, pos=None):
        self.pos = pos
        self.value = value
        self.child = None

    @property
    def nodes(self):
        l = [self]

        if self.child:
            l.extend(self.child.nodes)

        return l

    def append(self, y):
        if self.child:
            self.child.append(y)
        else:
            self.nodes[-1].child = y

    def __str__(self):
        return '$%s\n' % self.value


def p_program_1(p):
    '''program : code_block'''
    p[0] = p[1]


def p_program_2(p):
    '''program : DOLLAR preprocessor_block'''
    p[0] = p[2]


def p_code_block_1(p):
    '''code_block : code'''
    p[0] = p[1]


def p_code_block_2(p):
    '''code_block : code_block code'''
    if p[1] is not None and p[2] is not None:
        p[0] = p[1]
        p[0].append(p[2])

    elif p[1] is not None:
        p[0] = p[1]

    elif p[2] is not None:
        p[0] = p[2]


def p_code_1(p):
    '''code : NEWLINE DOLLAR preprocessor_block'''
    p[0] = p[3]


def p_code_2(p):
    '''
    code : white_space
    '''
    p[0] = p[1]


def p_code_3(p):
    '''
    code : LPAREN
    | RPAREN
    | IF
    | ELSE
    | ENDIF
    | INCLUDE
    | ANYTHING
    | IDENTIFIER
    | COMMENT
    | EJECT
    | COND
    | NOCOND
    | INTERRUPT
    | NOT
    | DOLLAR
    | NEWLINE
    '''
    p[0] = TextNode(p[1], get_pos(p, 0))


def p_white_space_1(p):
    '''white_space : WHITESPACE'''
    p[0] = TextNode(p[1], get_pos(p, 0))


def p_white_space_2(p):
    '''white_space : white_space WHITESPACE'''
    p[0] = p[1]
    p[0].append(TextNode(p[2], get_pos(p, 0)))


def p_preprocessor_block_1(p):
    '''preprocessor_block : if_block'''
    p[0] = p[1]


def p_preprocessor_block_2(p):
    '''preprocessor_block : include_block'''
    p[0] = p[1]


def p_preprocessor_block_3(p):
    '''preprocessor_block : eject_block'''
    p[0] = p[1]


def p_preprocessor_block_4(p):
    '''preprocessor_block : cond_block'''
    p[0] = p[1]


def p_preprocessor_block_5(p):
    '''preprocessor_block : interrupt_block'''
    p[0] = p[1]


def p_if_block_start_1(p):
    '''if_block_start : IF white_space IDENTIFIER'''
    global pre_defines
    key = p[3].lower()
    if key in pre_defines.keys():
        p[0] = pre_defines[key]
    else:
        p[0] = False


def p_if_block_start_2(p):
    '''if_block_start : IF white_space NOT white_space IDENTIFIER'''
    global pre_defines
    key = p[5].lower()
    if key in pre_defines.keys():
        p[0] = not pre_defines[key]
    else:
        p[0] = True


def p_if_block_end(p):
    '''if_block_end : NEWLINE DOLLAR ENDIF'''
    p[0] = DirectiveNode(p[3], get_pos(p, 0))


def p_if_block_else(p):
    '''if_block_else : NEWLINE DOLLAR ELSE'''
    p[0] = DirectiveNode(p[3], get_pos(p, 0))


def p_if_block_1(p):
    '''if_block : if_block_start code_block if_block_end'''
    p[0] = DirectiveNode(p[1], get_pos(p, 0))

    if p[1]:
        p[0].append(p[2])

    p[0].append(p[3])


def p_if_block_2(p):
    '''
    if_block : if_block_start code_block if_block_else code_block if_block_end
    '''
    p[0] = DirectiveNode(p[1], get_pos(p, 0))

    if p[1]:
        p[0].append(p[2])
    else:
        p[0].append(p[4])

    p[0].append(p[5])


def p_eject_block_1(p):
    '''eject_block : EJECT'''
    p[0] = DirectiveNode(p[1], get_pos(p, 0))


def p_cond_block_1(p):
    '''cond_block : COND'''
    p[0] = DirectiveNode(p[1], get_pos(p, 0))


def p_cond_block_2(p):
    '''cond_block : NOCOND'''
    p[0] = DirectiveNode(p[1], get_pos(p, 0))


def p_interrupt_block_1(p):
    '''interrupt_block : INTERRUPT LPAREN IDENTIFIER RPAREN'''
    p[0] = DirectiveNode(p[1] + p[2] + p[3] + p[4], get_pos(p, 0))


def p_interrupt_block_2(p):
    '''interrupt_block : INTERRUPT white_space LPAREN IDENTIFIER RPAREN'''
    p[0] = DirectiveNode(p[1] + str(p[2]) + p[3] + p[4] + p[5], get_pos(p, 0))


def p_include_block_1(p):
    '''
    include_block : INCLUDE LPAREN IDENTIFIER RPAREN
    | INCLUDE white_space LPAREN IDENTIFIER RPAREN
    '''

    if len(p) == 6:
        s = p[1] + str(p[2]) + p[3] + p[4] + p[5]
    else:
        s = p[1] + p[2] + p[3] + p[4]

    p[0] = DirectiveNode(s, get_pos(p, 0))

    global pre_includes

    if len(p) == 5:
        filename = p[3]
    else:
        filename = p[4]

    for path in pre_includes:
        file_ = path + '/' + filename
        if os.path.exists(file_):
            p[0].append(process(file_, filename))
            return

    log.e("pre", "Cannot include '%s'" % filename)


def p_error(p):
    if p:
        log.e("pre", "invalid token '%s' at (%d, %d)" %
                     (p.value, p.lineno, p.lexpos))
    else:
        log.e("pre", "unknown error")


def get_pos(p, num):

    global pre_filename
    file_ = list(pre_filename)
    line = p.lineno(num)
    span = p.lexspan(num)

    return (file_, line, span[0], span[1])


def scanner(debug=False):
    if debug:
        logger = lex.PlyLogger(sys.stderr)
    else:
        logger = lex.NullLogger()

    tab = "llvm_p86._p86pre_lextab"
    mod = sys.modules[__name__]
    return lex.lex(debuglog=logger,
                   errorlog=logger,
                   optimize=1,
                   lextab=tab,
                   outputdir=os.path.dirname(__file__),
                   module=mod)


def parser(debug=False):
    if debug:
        logger = yacc.PlyLogger(sys.stderr)
    else:
        logger = yacc.NullLogger()

    tab = "llvm_p86._p86pre_parsetab"
    mod = sys.modules[__name__]
    return yacc.yacc(debuglog=logger,
                     errorlog=logger,
                     optimize=1,
                     tabmodule=tab,
                     outputdir=os.path.dirname(__file__),
                     module=mod)


def process(filepath, filename=None):
    log.d("pre", "Processing %s" % filepath)
    path = os.path.dirname(filepath)

    if not filename:
        filename = os.path.basename(filepath)

    global pre_includes
    global pre_filename

    pre_includes.append(path)
    pre_filename.append(filename)

    s = scanner(False)
    p = parser(False)

    data = _get_character_stream(filepath)
    chars = p.parse(input=data, lexer=s, tracking=True)

    log.d("pre", "Processing %s completed" % filename)

    pre_includes.pop()
    pre_filename.pop()

    return chars
