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
Type generator for Pascal-86 syntax trees.
'''

import copy

from . import ast
from . import symtab
from . import log


def log_prefix(node):
    pos = node.position
    if not pos:
        pos = '?'

    return node.__class__.__name__ + ':' + str(pos)


def _upcast_ret(lhs=None, rhs=None):
    if not rhs:
        return lhs, lhs
    else:
        return lhs, rhs


def upcast_int(lhs, rhs):
    '''
    make sure lhs and rhs is of the same integer type.
    upcasts to the smallest possible width. when signess differ,
    the largest width * 2 will be used.
    '''
    if not isinstance(lhs, symtab.IntType):
        return _upcast_ret()
    if not isinstance(rhs, symtab.IntType):
        return _upcast_ret()

    if (lhs.value is not None and
        rhs.lo <= lhs.value <= rhs.hi):
        return _upcast_ret(rhs)

    elif (rhs.value is not None and
        lhs.lo <= rhs.value <= lhs.hi):
        return _upcast_ret(lhs)

    elif lhs.signed == rhs.signed:
        if lhs.width >= rhs.width:
            return _upcast_ret(lhs)
        else:
            return _upcast_ret(rhs)

    elif lhs.signed and rhs.unsigned:
        if lhs.width > rhs.width:
            width = lhs.width
        else:
            width = rhs.width * 2

        return _upcast_ret(symtab.SIntType(width))

    elif lhs.unsigned and rhs.signed:
        if lhs.width < rhs.width:
            width = rhs.width
        else:
            width = lhs.width * 2

        return _upcast_ret(symtab.SIntType(width))

    else:
        return _upcast_ret()


def upcast_real(lhs, rhs):
    '''
    upcast lhs and rhs to a real number.
    NOTE: assumes that all integers (signed or unsigned) will fit
    inside a float.
    '''
    if (isinstance(lhs, symtab.RealType) and
        isinstance(rhs, symtab.RealType)):
        if lhs.width >= rhs.width:
            return _upcast_ret(lhs)
        else:
            return _upcast_ret(rhs)

    elif isinstance(lhs, symtab.RealType):
        return _upcast_ret(lhs)

    elif isinstance(rhs, symtab.RealType):
        return _upcast_ret(rhs)

    else:
        return _upcast_ret(symtab.FloatType())


def upcast(lhs, rhs):
    if lhs == rhs:
        return _upcast_ret(lhs, rhs)

    elif isinstance(lhs, symtab.AnyType):
        return _upcast_ret(rhs)

    elif isinstance(rhs, symtab.AnyType):
        return _upcast_ret(lhs)

    elif (isinstance(lhs, symtab.RealType) or
        isinstance(rhs, symtab.RealType)):
        return upcast_real(lhs, rhs)

    elif (isinstance(lhs, symtab.IntType) and
        isinstance(rhs, symtab.IntType)):
        return upcast_int(lhs, rhs)

    elif (isinstance(lhs, symtab.SetType) and
        isinstance(rhs, symtab.EmptySetType)):
        return _upcast_ret(lhs)

    elif (isinstance(lhs, symtab.EmptySetType) and
        isinstance(rhs, symtab.SetType)):
        return _upcast_ret(rhs)

    elif (isinstance(lhs, symtab.PointerType) and
        isinstance(rhs, symtab.PointerType) and
        isinstance(lhs.pointee, symtab.AnyType)):
        return _upcast_ret(rhs)

    elif (isinstance(lhs, symtab.PointerType) and
        isinstance(rhs, symtab.PointerType) and
        isinstance(rhs.pointee, symtab.AnyType)):
        return _upcast_ret(lhs)

    elif (isinstance(lhs, symtab.SetType) and
        isinstance(rhs, symtab.SetType)):
        lo = min(lhs.element.lo, rhs.element.lo)
        hi = max(lhs.element.hi, rhs.element.hi)

        if (isinstance(lhs.element, symtab.IntType) and
            isinstance(rhs.element, symtab.IntType)):
            el_ty = symtab.IntRangeType(lo, hi)
        elif (isinstance(lhs.element, symtab.CharType) and
              isinstance(rhs.element, symtab.CharType)):
            el_ty = symtab.CharRangeType(lo, hi)
        else:
            return _upcast_ret()

        return _upcast_ret(symtab.SetType(el_ty))

    else:
        return _upcast_ret()


def upcast_arithmetic(lhs, rhs, sign=None):

    if sign == '/':
        return _upcast_ret(symtab.TempRealType())

    elif (isinstance(lhs, symtab.RealType) or
        isinstance(rhs, symtab.RealType)):
        if sign in ['div', 'mod']:
            return _upcast_ret()
        else:
            return _upcast_ret(symtab.TempRealType())

    def _int_prepare(x):
        if isinstance(x, symtab.IntType):
            x.value = None

            if x.width < 16:
                if x.signed:
                    x = symtab.SIntType(16)
                else:
                    x = symtab.UIntType(16)

        return x

    lhs = _int_prepare(lhs)
    rhs = _int_prepare(rhs)

    return upcast(lhs, rhs)


def upcast_relational(lhs, rhs, sign=None):

    # upcast left hand operator to set member
    if ((isinstance(lhs, symtab.IntType) or
         isinstance(lhs, symtab.CharType)) and
        isinstance(rhs, symtab.SetType) and
        sign == 'in'):
        return _upcast_ret(rhs.element, rhs)

    elif ((isinstance(lhs, symtab.IntType) or
         isinstance(lhs, symtab.CharType)) and
        isinstance(rhs, symtab.EmptySetType) and
        sign == 'in'):
        return _upcast_ret(lhs, symtab.SetType(lhs))

    elif sign == 'in':
        return _upcast_ret()

    return upcast(lhs, rhs)


class NodeException(Exception):

    def __init__(self, node, msg):
        Exception.__init__(self)
        self.msg = msg
        self.node = node

    def __str__(self):
        pos = self.node.position
        if not pos:
            pos = '?'

        return str(pos) + ':' + str(self.msg)


def downcast_assignment(source, target, pos):

    if source == target:
        return target

    # Int --> Int
    if (isinstance(source, symtab.IntType) and
        isinstance(target, symtab.IntType)):

        # Avoid warning message
        if (source.hi <= target.hi and
            source.lo >= target.lo):
            return target

        if(source.value is not None and
           target.lo <= source.value and
           target.hi >= source.value):
            return target

        if source.value:
            source = source.value

        log.w('typesys', "%s:casting from '%s' to '%s'" % (pos, source,
                                                           target))
        return target

    # Int --> Real
    elif (isinstance(source, symtab.IntType) and
        isinstance(target, symtab.RealType)):
        return target

    # Real --> Real
    elif (isinstance(source, symtab.RealType) and
          isinstance(target, symtab.RealType)):
            return target

    # Set --> Set
    elif (isinstance(source, symtab.SetType) and
          isinstance(target, symtab.SetType)):
        return target

    # EmptySet --> Set
    elif (isinstance(source, symtab.EmptySetType) and
          isinstance(target, symtab.SetType)):
        return target

    # Any
    elif (isinstance(target, symtab.AnyType)):
        return source

    # Any
    elif (isinstance(source, symtab.AnyType)):
        return target

    # Reference --> Reference of Any
    elif (isinstance(source, symtab.ReferenceType) and
          isinstance(target, symtab.ReferenceType) and
          isinstance(target.referee, symtab.AnyType)):
        return target

    # Array --> Reference of Any
    elif (isinstance(source, symtab.ArrayType) and
          isinstance(target, symtab.ReferenceType) and
          isinstance(target.referee, symtab.AnyType)):
        return target

    # Pointer --> Pointer of Any
    elif (isinstance(source, symtab.PointerType) and
          isinstance(target, symtab.PointerType) and
          isinstance(target.pointee, symtab.AnyType)):
        return target

    # Pointer of Any (Null) --> Pointer
    elif (isinstance(source, symtab.PointerType) and
          isinstance(target, symtab.PointerType) and
          isinstance(source.pointee, symtab.AnyType)):
        return target

    # Reference --> Reference
    elif (isinstance(source, symtab.ReferenceType) and
          isinstance(target, symtab.ReferenceType) and
          source.referee.width == target.referee.width and
          downcast_assignment(source.referee, target.referee, pos)):
        return target

    # Array --> Array (within range, same type width)
    elif (isinstance(source, symtab.ArrayType) and
          isinstance(target, symtab.ArrayType) and
          source.element.width == target.element.width and
          source.length <= target.length):
        return target

    return None


class ConstantEvalVisitor(ast.DefaultP86Visitor):

    def __init__(self, ctx):
        self.ctx = ctx

    def default_visit(self, node, arg=None):
        value = ast.DefaultP86Visitor.default_visit(self, node, arg)
        if value is None:
            return node
        else:
            return value

    def visit_UnaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.UnaryOpNode)

        expr = node.expr.accept(self)

        if isinstance(expr, ast.Node):
            raise NodeException(expr, "illegal constant expression")

        if node.name == '-':
            op = lambda val: (-val)
        elif node.name == '+':
            op = lambda val: (+val)
        elif node.name == 'not':
            op = lambda val: (~val)
        else:
            raise NodeException(node, "unknown unary operator '%s'" %
                                      node.name)

        return op(expr)

    def visit_OpNode(self, node, arg=None):
        assert isinstance(node, ast.OpNode)

        if node.name == '+':
            return lambda lhs, rhs: (lhs + rhs)
        if node.name == '-':
            return lambda lhs, rhs: (lhs - rhs)
        if node.name == '*':
            return lambda lhs, rhs: (lhs * rhs)
        if node.name == 'or':
            return lambda lhs, rhs: (lhs | rhs)
        if node.name == '/':
            return lambda lhs, rhs: (lhs / rhs)
        if node.name == 'div':
            return lambda lhs, rhs: (int(lhs) / int(rhs))
        if node.name == 'mod':
            return lambda lhs, rhs: (lhs % rhs)
        if node.name == 'and':
            return lambda lhs, rhs: (lhs & rhs)
        if node.name == '=':
            return lambda lhs, rhs: (lhs == rhs)
        if node.name == '<>':
            return lambda lhs, rhs: (lhs != rhs)
        if node.name == '<':
            return lambda lhs, rhs: (lhs < rhs)
        if node.name == '<=':
            return lambda lhs, rhs: (lhs <= rhs)
        if node.name == '>':
            return lambda lhs, rhs: (lhs > rhs)
        if node.name == '>=':
            return lambda lhs, rhs: (lhs >= rhs)

        raise NodeException(node, "unknown binary operator '%s'" % node.name)

    def visit_BinaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.BinaryOpNode)

        left = node.left.accept(self)
        right = node.right.accept(self)

        if isinstance(left, ast.Node):
            raise NodeException(left, "illegal constant expression")

        if isinstance(right, ast.Node):
            raise NodeException(right, "illegal constant expression")

        op = node.op.accept(self)

        return op(left, right)

    def visit_RangeNode(self, node, arg=None):
        assert isinstance(node, ast.RangeNode)

        node.start = node.start.accept(self, arg)
        node.stop = node.stop.accept(self, arg)

        return node

    def visit_CaseConstNode(self, node, arg=None):
        assert isinstance(node, ast.CaseConstNode)

        return node.constant.accept(self, arg)

    def visit_IntegerNode(self, node, arg=None):
        assert isinstance(node, ast.IntegerNode)

        return node.value

    def visit_RealNode(self, node, arg=None):
        assert isinstance(node, ast.RealNode)

        return node.value

    def visit_StringNode(self, node, arg=None):
        assert isinstance(node, ast.StringNode)

        return node.value

    def visit_CharNode(self, node, arg=None):
        assert isinstance(node, ast.CharNode)

        return node.value

    def visit_VarLoadNode(self, node, arg=None):
        assert isinstance(node, ast.VarLoadNode)

        return node.var_access.accept(self)

    def visit_VarAccessNode(self, node, field):
        assert isinstance(node, ast.VarAccessNode)

        if not isinstance(node.identifier, ast.IdentifierNode):
            raise NodeException(node, "illegal constant expression")

        sym = self.ctx.find_symbol(node.identifier.name)

        return sym.handle

    def visit_TypeConvertNode(self, node, field):
        assert isinstance(node, ast.TypeConvertNode)

        return node.child.accept(self)



class DeferredTypeVisitor(ast.DefaultP86Visitor):

    def __init__(self, ctx):
        self.ctx = ctx

    def default_visit(self, node, arg=None):
        # Ugly monkey patching required when named types are used
        # before being defined.
        if isinstance(node.type, symtab.DeferredType):
            ty = self.ctx.find_typedef(node.type.name)
            node.type.__class__ = ty.__class__
            node.type.__dict__ = ty.__dict__

        for c in node.children:
            if c is not None:
                c.accept(self)


class TypeSetVisitor(ast.DefaultP86Visitor):

    def __init__(self):
        self.ctx = symtab.SymbolTable()
        self.module = None
        self.ctx.enter_scope()
        self.func_scope_level = 0

        self.ctx.install_typedef('boolean' , symtab.BoolType())
        self.ctx.install_typedef('char'    , symtab.CharType())
        self.ctx.install_typedef('integer' , symtab.SIntType(16))
        self.ctx.install_typedef('word'    , symtab.UIntType(16))
        self.ctx.install_typedef('longint' , symtab.SIntType(32))
        self.ctx.install_typedef('longreal', symtab.DoubleType())
        self.ctx.install_typedef('real'    , symtab.FloatType())
        self.ctx.install_typedef('tempreal', symtab.TempRealType())
        self.ctx.install_typedef('bytes'   , symtab.AnyType())

        self.ctx.install_const('cr'        , symtab.CharType('\r')  , '\r')
        self.ctx.install_const('false'     , symtab.BoolType(False)  , False)
        self.ctx.install_const('lf'        , symtab.CharType('\n')  , '\n')
        self.ctx.install_const('maxint'    , symtab.SIntType(16, (2 ** 15) - 1), (2 ** 15) - 1)
        self.ctx.install_const('maxlongint', symtab.SIntType(32, (2 ** 31) - 1), (2 ** 31) - 1)
        self.ctx.install_const('maxword'   , symtab.UIntType(16, (2 ** 16) - 1), (2 ** 16) - 1)
        self.ctx.install_const('true'      , symtab.BoolType(True)  , True)

        # pointer --> VOID
        ty = symtab.FunctionType('P86', 'new')
        param = symtab.AnyType()
        param = symtab.ReferenceType(param)
        param = symtab.ParameterType('ptr', param)
        ty.params.append(param)
        self.ctx.install_function(ty.name, ty)

        # pointer --> VOID
        ty = symtab.FunctionType('P86', 'dispose')
        param = symtab.AnyType()
        param = symtab.ReferenceType(param)
        param = symtab.ParameterType('ptr', param)
        ty.params.append(param)
        self.ctx.install_function(ty.name, ty)

        # ordinal --> INTEGER
        ty = symtab.FunctionType('P86', 'ord', symtab.SIntType(16))
        ty.params.append(symtab.ParameterType(ty.name, symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # ordinal --> LONGINT
        ty = symtab.FunctionType('P86', 'lord', symtab.SIntType(32))
        ty.params.append(symtab.ParameterType('ordinal', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # ordinal --> WORD
        ty = symtab.FunctionType('P86', 'wrd', symtab.UIntType(16))
        ty.params.append(symtab.ParameterType('ordinal', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # int-type --> CHAR
        ty = symtab.FunctionType('P86', 'chr', symtab.CharType())
        ty.params.append(symtab.ParameterType('int', symtab.SIntType(32)))
        self.ctx.install_function(ty.name, ty)

        # TODO: ordinal --> same as input
        ty = symtab.FunctionType('P86', 'pred', symtab.AnyType())
        ty.params.append(symtab.ParameterType('ordinal', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # TODO: ordinal --> same as input
        ty = symtab.FunctionType('P86', 'succ', symtab.AnyType())
        ty.params.append(symtab.ParameterType('ordinal', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # int-type --> BOOLEAN
        ty = symtab.FunctionType('P86', 'odd', symtab.BoolType())
        ty.params.append(symtab.ParameterType('int', symtab.SIntType(32)))
        self.ctx.install_function(ty.name, ty)

        # TODO: int,real --> same as input
        ty = symtab.FunctionType('P86', 'abs', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('number', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TODO: int,real --> same as input
        ty = symtab.FunctionType('P86', 'sqr', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('number', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'sqrt', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'exp', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'ln', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'sin', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'cos', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'tan', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'arcsin', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'arccos', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # TEMPREAL --> TEMPREAL
        ty = symtab.FunctionType('P86', 'arctan', symtab.TempRealType())
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # real --> INTEGER
        ty = symtab.FunctionType('P86', 'trunc', symtab.SIntType(16))
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # real --> LONGINT
        ty = symtab.FunctionType('P86', 'ltrunc', symtab.SIntType(32))
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # real --> INTEGER
        ty = symtab.FunctionType('P86', 'round', symtab.SIntType(16))
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # real --> LONGINT
        ty = symtab.FunctionType('P86', 'lround', symtab.SIntType(32))
        ty.params.append(symtab.ParameterType('real', symtab.TempRealType()))
        self.ctx.install_function(ty.name, ty)

        # any --> WORD
        ty = symtab.FunctionType('P86', 'size', symtab.UIntType(32))
        ty.params.append(symtab.ParameterType('x', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # WORD --> WORD
        ty = symtab.FunctionType('P86', 'paramstr', symtab.UIntType(16))
        ty.params.append(symtab.ParameterType('x', symtab.UIntType(16)))
        self.ctx.install_function(ty.name, ty)

        # void --> WORD
        ty = symtab.FunctionType('P86', 'paramcount', symtab.UIntType(32))
        self.ctx.install_function(ty.name, ty)

        # variadic functions
        ty = symtab.FunctionType('P86', 'write')
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'writeln')
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'read', symtab.SIntType(32))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'readln', symtab.SIntType(32))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'halt')
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'inbyt')
        ty.params.append(symtab.ParameterType('addr', symtab.SIntType(16)))
        ty.params.append(symtab.ParameterType('b', symtab.ReferenceType(symtab.AnyType())))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'inwrd')
        ty.params.append(symtab.ParameterType('addr', symtab.SIntType(16)))
        ty.params.append(symtab.ParameterType('w', symtab.ReferenceType(symtab.AnyType())))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'outbyt')
        ty.params.append(symtab.ParameterType('addr', symtab.SIntType(16)))
        ty.params.append(symtab.ParameterType('b', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'outwrd')
        ty.params.append(symtab.ParameterType('addr', symtab.SIntType(16)))
        ty.params.append(symtab.ParameterType('w', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'setinterrupt')
        ty.params.append(symtab.ParameterType('num', symtab.UIntType(16)))
        ty.params.append(symtab.ParameterType('proc', symtab.AnyType()))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'enableinterrupts')
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'disableinterrupts')
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'causeinterrupt')
        ty.params.append(symtab.ParameterType('num', symtab.UIntType(8)))
        self.ctx.install_function(ty.name, ty)

        # builtin mutation functions
        ty = symtab.FunctionType('P86', 'setmutation')
        ty.params.append(symtab.ParameterType('x', symtab.SIntType(32)))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'setmutationid')
        ty.params.append(symtab.ParameterType('idx', symtab.SIntType(32)))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'getmutationid', symtab.SIntType(32))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'getmutationmod', symtab.StringType(0))
        self.ctx.install_function(ty.name, ty)

        ty = symtab.FunctionType('P86', 'getmutationcount', symtab.SIntType(32))
        self.ctx.install_function(ty.name, ty)

    def visit(self, node, arg=None):
        try:
            return ast.DefaultP86Visitor.visit(self, node, arg)
        except NodeException as e:
            log.e('typesys', str(e))
        except symtab.SymtabException as e:
            log.e('typesys', str(e))

    def visit_ProgramNode(self, node, arg=None):
        assert isinstance(node, ast.ProgramNode)

        self.module = node.identifier.accept(self)

        self.ctx.enter_scope()

        if node.block:
            node.block.accept(self)

        self.ctx.exit_scope()

    def visit_ModuleNode(self, node, arg=None):
        assert isinstance(node, ast.ModuleNode)

        self.ctx.enter_scope()

        self.module = node.identifier.accept(self)

        if node.interface:
            node.interface.accept(self)

        if node.entry_point:
            node.entry_point.accept(self)

        self.ctx.exit_scope()

    def visit_PublicSectionNode(self, node, arg=None):
        assert isinstance(node, ast.PublicSectionNode)

        module = node.identifier.accept(self)

        if node.section:
            node.section.accept(self, module)

    def visit_PublicFunctionNode(self, node, module):
        assert isinstance(node, ast.PublicFunctionNode)

        func = node.heading.accept(self, module)
        self.ctx.install_function(func.name, func)

        node.type = func.ret

        return node.type

    def visit_PublicProcedureNode(self, node, module):
        assert isinstance(node, ast.PublicProcedureNode)

        func = node.heading.accept(self, module)
        self.ctx.install_function(func.name, func)

        node.type = func.ret

        return node.type

    def visit_FunctionNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionNode)

        func = node.header.accept(self, self.module)
        node.type = func.ret

        self.ctx.install_function(func.name, func)

        self.func_scope_level += 1
        self.ctx.enter_scope()

        for param in func.params:
            self.ctx.install_symbol(param.name, param.type)

        self.ctx.install_symbol(func.name, func.ret)

        if node.block:
            node.block.accept(self)

        self.ctx.exit_scope()
        self.func_scope_level -= 1

        return node.type

    def visit_ProcedureNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureNode)

        func = node.header.accept(self, self.module)
        node.type = symtab.VoidType()

        self.ctx.install_function(func.name, func)

        self.func_scope_level += 1
        self.ctx.enter_scope()

        for param in func.params:
            self.ctx.install_symbol(param.name, param.type)

        if node.block:
            node.block.accept(self)

        self.ctx.exit_scope()
        self.func_scope_level -= 1

        return node.type

    def visit_WithNode(self, node, arg=None):
        assert isinstance(node, ast.WithNode)

        self.ctx.enter_scope()

        for rec in node.rec_var_list.accept(self):
            for field in rec.fields:
                self.ctx.install_symbol(field.name, field.type)

            if rec.variant is None:
                continue

            if rec.variant.selector:
                selector = rec.variant.selector
                self.ctx.install_symbol(selector.name, selector.type)

            for case in rec.variant.cases:
                for field in case.fields:
                    self.ctx.install_symbol(field.name, field.type)

        if node.statement_list:
            node.statement_list.accept(self)

        self.ctx.exit_scope()

    def visit_IndexedVarNode(self, node, field=None):
        assert isinstance(node, ast.IndexedVarNode)

        ty = node.var_access.accept(self)
        indices = node.index_expr_list.accept(self)

        for _ in indices:
            if not isinstance(ty, symtab.ArrayType):
                raise NodeException(node, "variable type '%s' is not indexed" %
                                          ty)

            ty = ty.element

        node.type = ty

        return node.type

    def visit_PointerAccessNode(self, node, field):
        assert isinstance(node, ast.PointerAccessNode)

        ty = node.var_access.accept(self)

        if not isinstance(ty, symtab.PointerType):
            raise NodeException(node, "variable type '%s' is not a pointer" %
                                      ty)

        node.type = ty.pointee

        return node.type

    def visit_VarAccessNode(self, node, field):
        assert isinstance(node, ast.VarAccessNode)

        name = node.identifier.accept(self)

        try:
            sym = self.ctx.find_symbol(name)
        except symtab.SymtabException:
            try:
                sym = self.ctx.find_function(name)
                return sym.type.ret
            except symtab.SymtabException:
                raise NodeException(node, "call to unknown function '%s'" %
                                          name)

        if isinstance(sym.type, symtab.ReferenceType):
            node.type = sym.type.referee
        else:
            node.type = sym.type

        return node.type

    def visit_FieldAccessNode(self, node, arg=None):
        assert isinstance(node, ast.FieldAccessNode)

        name = node.identifier.accept(self)
        var = node.var_access.accept(self)

        for field in var.fields:
            if field.name == name:
                node.type = field.type
                return node.type

        if var.variant:
            s = var.variant.selector
            if s and s.name == name:
                node.type = s.type
                return node.type

            for case in var.variant.cases:
                for field in case.fields:
                    if field.name == name:
                        node.type = field.type
                        return node.type

        raise NodeException(node, "unknown field '%s'" % name)

    def visit_VarLoadNode(self, node, arg=None):
        assert isinstance(node, ast.VarLoadNode)

        ty = node.var_access.accept(self)

        if isinstance(ty, symtab.ReferenceType):
            node.type = ty.referee
        else:
            node.type = ty

        return node.type

    def visit_UnaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.UnaryOpNode)

        signed = node.name in ['+', '-']

        ty = node.expr.accept(self, signed)

        if (isinstance(ty, symtab.IntType) and
            not ty.signed and signed):
            ty = symtab.SIntType(32)

            node.expr = ast.TypeConvertNode(node.expr)
            node.expr.type = ty

        node.type = ty

        return node.type

    def visit_BinaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.BinaryOpNode)

        sign = node.op.name

        left = node.left.accept(self)
        right = node.right.accept(self)

        if sign in ['+', '-', '*', '/', 'div', 'mod']:
            lhs, rhs = upcast_arithmetic(left, right, sign)
            if not lhs or not rhs:
                raise NodeException(node, "invalid binary expression '%s' '%s' '%s'" % (left, sign, right))

            if lhs != left:
                node.left = ast.TypeConvertNode(node.left)
                node.left.type = lhs

            if rhs != right:
                node.right = ast.TypeConvertNode(node.right)
                node.right.type = rhs

            assert lhs == rhs
            ty = lhs

        elif sign in ['=', '<>', '>', '>=', '<', '<=', 'in']:
            lhs, rhs = upcast_relational(left, right, sign)
            if not lhs or not rhs:
                raise NodeException(node, "invalid binary expression '%s' '%s' '%s'" % (left, sign, right))

            if lhs != left:
                node.left = ast.TypeConvertNode(node.left)
                node.left.type = lhs

            if rhs != right:
                node.right = ast.TypeConvertNode(node.right)
                node.right.type = rhs

            ty = symtab.BoolType()

        elif sign in ['and', 'or']:
            if (not isinstance(left, symtab.BoolType) or
                not isinstance(right, symtab.BoolType)):
                raise NodeException(node, "invalid binary expression '%s' '%s' '%s'" % (left, sign, right))

            ty = symtab.BoolType()

        node.type = ty

        return node.type

    def visit_AssignmentNode(self, node, arg=None):
        assert isinstance(node, ast.AssignmentNode)

        left = node.var_access.accept(self)
        right = node.expr.accept(self)

        ty = downcast_assignment(right, left, node.position)
        if ty is None:
            raise NodeException(node, "casting from '%s' to '%s'" %
                                      (right, left))

        elif ty != right:
            node.expr = ast.TypeConvertNode(node.expr)
            node.expr.type = ty

        node.type = ty

        return node.type

    def visit_FunctionCallNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionCallNode)

        name = node.identifier.accept(self)

        try:
            sym = self.ctx.find_function(name)
            params = list(sym.type.params)

            if node.arg_list:
                args = node.arg_list.accept(self, params)
            else:
                args = []

            if len(params):
                raise NodeException(node, "wrong number of arguments to '%s'" %
                                          name)

            node.type = sym.type.ret
            return node.type

        except symtab.SymtabException:
            pass

        try:
            ty = self.ctx.find_typedef(name)

            if not node.arg_list:
                raise NodeException(node, "wrong number of arguments to '%s'" %
                                          name)

            args = node.arg_list.accept(self)
            if len(args) != 1:
                raise NodeException(node, "wrong number of arguments to '%s'" %
                                          name)

        except symtab.SymtabException:
            raise NodeException(node, "call to unknown function '%s'" % name)

        node.type = ty

        return node.type

    def visit_ArgumentNode(self, node, params=None):
        assert isinstance(node, ast.ArgumentNode)

        expr = node.expr.accept(self)

        if params and len(params):
            p = params.pop(0)

            if isinstance(p.type, symtab.ReferenceType):
                if isinstance(node.expr, ast.VarLoadNode):
                    node.expr = ast.VarReferenceNode(node.expr.var_access)
                    node.expr.type = symtab.ReferenceType(expr)
                    expr = node.expr.type
                elif isinstance(expr, symtab.ArrayType):
                    pass
                else:
                    raise NodeException(node, "argument is not referenceable")

            ty = downcast_assignment(expr, p.type, node.position)
            if ty is None:
                raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                          (expr, p.type))
            elif ty != expr:
                node.expr = ast.TypeConvertNode(node.expr)
                node.expr.type = ty

            node.type = ty

        else:
            node.type = expr

        if hasattr(expr, 'value'):
            node.type.value = expr.value

        return node.type

    def visit_ForNode(self, node, arg=None):
        assert isinstance(node, ast.ForNode)

        name = node.var.accept(self)
        sym = self.ctx.find_symbol(name)

        start = node.value_start.accept(self)
        end = node.value_end.accept(self)

        node.body.accept(self)  # populate with type info

        ty = downcast_assignment(start, sym.type, node.value_start.position)
        if ty is None:
            raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                      (start, sym.type))

        elif ty != start:
            node.value_start = ast.TypeConvertNode(node.value_start)
            node.value_start.type = ty

        ty = downcast_assignment(end, sym.type, node.value_end.position)
        if ty is None:
            raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                      (end, sym.type))

        elif ty != end:
            node.value_end = ast.TypeConvertNode(node.value_end)
            node.value_end.type = ty

    ######################################
    # Single values                      #
    ######################################

    def visit_IntegerNode(self, node, signed=False):
        assert isinstance(node, ast.IntegerNode)

        if node.value > (2 ** 63) - 1:
            ty = symtab.UIntType(64, node.value)
        elif node.value > (2 ** 32) - 1:
            ty = symtab.SIntType(64, node.value)
        elif node.value > (2 ** 31) - 1:
            ty = symtab.UIntType(32, node.value)
        elif node.value > (2 ** 16) - 1:
            ty = symtab.SIntType(32, node.value)
        elif node.value > (2 ** 15) - 1:
            ty = symtab.UIntType(16, node.value)
        else:
            ty = symtab.SIntType(16, node.value)

        node.type = ty

        return node.type

    def visit_RealNode(self, node, arg=None):
        assert isinstance(node, ast.RealNode)

        if node.value > (2 ** 31) - 1:
            node.type = symtab.DoubleType()
        else:
            node.type = symtab.FloatType()

        return node.type

    def visit_StringNode(self, node, arg=None):
        assert isinstance(node, ast.StringNode)

        length = len(node.value)
        node.type = symtab.StringType(length)

        return node.type

    def visit_CharNode(self, node, arg=None):
        assert isinstance(node, ast.CharNode)

        node.type = symtab.CharType()
        node.type.value = node.value

        return node.type

    def visit_SetMemberRangeNode(self, node, arg=None):
        assert isinstance(node, ast.SetMemberRangeNode)

        member = node.member.accept(self)
        stop = node.expr.accept(self)

        if member != stop:
            ty, _ = upcast_int(member, stop)
            if ty is None:
                raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                          (member, stop))
        else:
            ty = member

        node.type = ty

        return node.type

    def visit_SetNode(self, node, arg=None):
        assert isinstance(node, ast.SetNode)

        members = node.member_list.accept(self)
        if len(members) == 0:
            raise NodeException(node, "invalid set range")

        values = []
        for m in members:
            if m.value is not None:
                values.append(m.value)
            else:
                values.append(m.lo)
                values.append(m.hi)

        lo = min(values)
        hi = max(values)

        if all(isinstance(x, int) for x in values):
            el_ty = symtab.IntRangeType(lo, hi)
        elif all(isinstance(x, int) for x in values):
            el_ty = symtab.CharRangeType(lo, hi)
        else:
            raise NodeException(node, "invalid set range")

        node.type = symtab.SetType(el_ty)

        return node.type

    def visit_SetEmptyNode(self, node, arg=None):
        assert isinstance(node, ast.SetEmptyNode)

        node.type = symtab.EmptySetType()

        return node.type

    ######################################
    # Definitions and declarations       #
    ######################################

    def visit_RangeNode(self, node, arg=None):
        assert isinstance(node, ast.RangeNode)

        lo = node.start.accept(self)
        hi = node.stop.accept(self)

        if lo != hi:
            ty_lo, ty_hi = upcast_int(lo, hi)
        else:
            ty_lo, ty_hi = lo, hi

        if (not ty_lo) or (not ty_hi):
            raise NodeException(node, "invalid range combo '%s' and '%s'" %
                                      (lo, hi))

        if ty_lo != lo:
            node.start = ast.TypeConvertNode(node.start)
            node.start.type = ty_lo

        if ty_hi != hi:
            node.stop = ast.TypeConvertNode(node.stop)
            node.stop.type = ty_hi

        cev = ConstantEvalVisitor(self.ctx)
        lo = node.start.accept(cev)
        hi = node.stop.accept(cev)

        if isinstance(lo, str) and len(lo) != 1:
            raise NodeException(node.start, "invalid range type '%s'" % lo)

        if isinstance(hi, str) and len(hi) != 1:
            raise NodeException(node.stop, "invalid range type '%s'" % hi)

        if isinstance(hi, str):
            node.type = symtab.CharRangeType(lo, hi)
        else:
            node.type = symtab.IntRangeType(lo, hi)

        return node.type

    def visit_ConstDeclNode(self, node, arg=None):
        assert isinstance(node, ast.ConstDeclNode)

        name = node.identifier.accept(self)
        ty = node.expr.accept(self)

        cev = ConstantEvalVisitor(self.ctx)
        value = node.expr.accept(cev)

        # convert 'a' + 'b' to 'ab'
        if isinstance(value, str) and len(value) > 1:
            ty = symtab.StringType(len(value))

        ty.value = value
        self.ctx.install_const(name, ty, value)

        node.type = ty

        return node.type

    def visit_EnumTypeNode(self, node, arg=None):
        assert isinstance(node, ast.EnumTypeNode)

        names = node.identifier_list.accept(self)

        for value, name in enumerate(names):
            ty = symtab.EnumType(names)
            ty.value = value
            self.ctx.install_const(name, ty, value)

        node.type = symtab.EnumType(names)

        return node.type

    def visit_SetTypeNode(self, node, arg=None):
        assert isinstance(node, ast.SetTypeNode)

        base = node.base_type.accept(self)
        ty = symtab.SetType(base)

        node.type = ty

        return node.type

    def visit_TypeNode(self, node, arg=None):
        assert isinstance(node, ast.TypeNode)

        name = node.identifier.accept(self)

        try:
            node.type = self.ctx.find_typedef(name)
        except symtab.SymtabException as e:
            node.type = symtab.DeferredType(name)

        return node.type


    def visit_TypeDeclListNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclListNode)

        for c in node.children:
            c.accept(self)

        for c in node.children:
            c.accept(DeferredTypeVisitor(self.ctx))


    def visit_ArrayTypeNode(self, node, arg=None):
        assert isinstance(node, ast.ArrayTypeNode)

        ty = node.component_type.accept(self)
        dims = node.index_list.accept(self)

        for dim in dims:
            ty = symtab.ArrayType(ty, dim)

        node.type = ty

        return node.type

    def visit_PointerTypeNode(self, node, arg=None):
        assert isinstance(node, ast.PointerTypeNode)

        pointee_ty = node.domain_type.accept(self)
        node.type = symtab.PointerType(pointee_ty)

        return node.type

    def visit_NullNode(self, node, ty):
        assert isinstance(node, ast.NullNode)

        pointee_ty = symtab.AnyType()
        node.type = symtab.PointerType(pointee_ty)

        return node.type

    def visit_FileTypeNode(self, node, arg=None):
        assert isinstance(node, ast.FileTypeNode)

        ty = node.component_type.accept(self)
        node.type = symtab.FileType(ty)

        return node.type

    def visit_TypeDeclNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclNode)

        name = node.identifier.accept(self)
        ty = node.type_denoter.accept(self)
        ty.name = name
        self.ctx.install_typedef(name, ty)

        node.type = ty

        return node.type

    def visit_VarDeclNode(self, node, arg=None):
        assert isinstance(node, ast.VarDeclNode)

        ty = node.type_denoter.accept(self)
        names = node.identifier_list.accept(self)

        for name in names:
            self.ctx.install_symbol(name, ty)

        node.type = ty

        return node.type

    def visit_FunctionHeadNode(self, node, module=None):
        assert isinstance(node, ast.FunctionHeadNode)

        name = node.identifier.accept(self)
        ret_ty = node.return_type.accept(self)

        ty = symtab.FunctionType(module, name, ret_ty, self.func_scope_level)

        if node.param_list:
            ty.params = node.param_list.accept(self)

        node.type = ty

        return node.type

    def visit_ProcedureHeadNode(self, node, module=None):
        assert isinstance(node, ast.ProcedureHeadNode)

        name = node.identifier.accept(self)
        ret_ty = symtab.VoidType()

        ty = symtab.FunctionType(module, name, ret_ty, self.func_scope_level)

        if node.param_list:
            ty.params = node.param_list.accept(self)

        node.type = ty

        return node.type

    def visit_ValueParameterNode(self, node, arg=None):
        assert isinstance(node, ast.ValueParameterNode)

        type_name = node.type_denoter.accept(self)
        ty = self.ctx.find_typedef(type_name)
        names = node.identifier_list.accept(self)

        l = []
        for name in names:
            param = symtab.ParameterType(name, ty)
            l.append(param)

        return l

    def visit_RefParameterNode(self, node, arg=None):
        assert isinstance(node, ast.RefParameterNode)

        type_name = node.type_denoter.accept(self)
        ty = self.ctx.find_typedef(type_name)
        ty = symtab.ReferenceType(ty)
        names = node.identifier_list.accept(self)

        l = []
        for name in names:
            param = symtab.ParameterType(name, ty)
            l.append(param)

        return l

    def visit_RecordTypeNode(self, node, arg=None):
        assert isinstance(node, ast.RecordTypeNode)

        name = self.ctx.label()
        ty = symtab.RecordType(name)

        if node.section_list:
            ty.fields = node.section_list.accept(self)

        if node.variant:
            ty.variant = node.variant.accept(self)

        node.type = ty

        return node.type

    def visit_RecordSectionNode(self, node, arg=None):
        assert isinstance(node, ast.RecordSectionNode)

        names = node.identifier_list.accept(self)
        ty = node.type_denoter.accept(self)

        fields = []
        for name in names:
            field = symtab.FieldType(name, ty)
            fields.append(field)

        node.type = ty

        return fields

    def visit_VariantPartNode(self, node, arg=None):
        assert isinstance(node, ast.VariantPartNode)

        name = self.ctx.label()
        ty = symtab.VariantType(name)

        ty.selector = node.variant_selector.accept(self)
        ty.cases = node.variant_list.accept(self, ty.selector)

        node.type = ty

        return node.type

    def visit_VariantSelectorNode(self, node, arg=None):
        assert isinstance(node, ast.VariantSelectorNode)

        if node.tag_field:
            field_name = node.tag_field.accept(self)
        else:
            field_name = self.ctx.label("selector")

        type_name = node.tag_type.accept(self)
        field_type = self.ctx.find_typedef(type_name)

        node.type = symtab.FieldType(field_name, field_type)

        return node.type

    def visit_VariantNode(self, node, selector):
        assert isinstance(node, ast.VariantNode)

        node.case_list.accept(self, selector.type)   # populate with type info

        cev = ConstantEvalVisitor(self.ctx)
        node.case_list.accept(cev)

        if node.variant_part:
            node.variant_part.accept(self)

        if node.record_list:
            record_name = self.ctx.label("variant")
            ty = symtab.RecordType(record_name)
            ty.fields = node.record_list.accept(self)

            return ty

    def visit_CaseStatementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseStatementNode)

        index = node.case_index.accept(self)
        node.case_list_element_list.accept(self, index)

        if node.otherwise:
            node.otherwise.accept(self)

        node.type = index

        return node.type

    def visit_CaseListElementNode(self, node, index):
        assert isinstance(node, ast.CaseListElementNode)

        consts = node.case_constant_list.accept(self, index)

        if node.statement:
            node.statement.accept(self)

        return consts

    def visit_CaseConstNode(self, node, index):
        assert isinstance(node, ast.CaseConstNode)

        const = node.constant.accept(self)

        lhs, rhs = upcast_relational(const, index)
        if index != rhs:
            raise NodeException(node, "casting from '%s' to '%s'" %
                                      (const, index))

        elif lhs != const:
            node.constant = ast.TypeConvertNode(node.constant)
            node.constant.type = lhs

        node.type = copy.deepcopy(lhs)
        node.type.value = const.value

        return node.type

    def visit_CaseRangeNode(self, node, index=None):
        assert isinstance(node, ast.CaseRangeNode)

        lo = node.first_constant.accept(self)
        hi = node.last_constant.accept(self)

        if lo != hi:
            ty_lo, ty_hi = upcast_int(lo, hi)
        else:
            ty_lo, ty_hi = lo, hi

        if (not ty_lo) or (not ty_hi):
            raise NodeException(node, "invalid range combination '%s' and '%s'" % (lo, hi))

        if ty_lo != lo:
            node.first_constant = ast.TypeConvertNode(node.first_constant)
            node.first_constant.type = ty_lo

        if ty_hi != hi:
            node.last_constant = ast.TypeConvertNode(node.last_constant)
            node.last_constant.type = ty_hi

        cev = ConstantEvalVisitor(self.ctx)
        lo = node.first_constant.accept(cev)
        hi = node.last_constant.accept(cev)

        if isinstance(lo, str) and len(lo) != 1:
            raise NodeException(node.start, "illegal range type '%s'" % lo)

        if isinstance(hi, str) and len(hi) != 1:
            raise NodeException(node.stop, "illegal range type '%s'" % hi)

        if isinstance(hi, str):
            node.type = symtab.CharRangeType(lo, hi)
        else:
            node.type = symtab.IntRangeType(lo, hi, index.width)

        return node.type

    def visit_IdentifierNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierNode)

        return node.name


class CallByRefVisitor(ast.NodeVisitor):

    def __init__(self):
        self.named_functions = dict()
        self.named_functions['read'] = [None]
        self.named_functions['readln'] = [None]

    def default_visit(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node, arg)

        return node

    def visit_ValueParameterNode(self, node, func=None):
        assert isinstance(node, ast.ValueParameterNode)

        for _ in node.identifier_list.children:
            self.named_functions[func].append(False)

    def visit_RefParameterNode(self, node, func=None):
        assert isinstance(node, ast.RefParameterNode)

        for _ in node.identifier_list.children:
            self.named_functions[func].append(True)

    def visit_IdentifierNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierNode)

        return node.name

    def visit_ProcedureHeadNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureHeadNode)

        name = node.identifier.accept(self)
        self.named_functions[name] = list()

        if node.param_list:
            node.param_list.accept(self, name)

    def visit_FunctionHeadNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionHeadNode)

        name = node.identifier.accept(self)
        self.named_functions[name] = list()

        if node.param_list:
            node.param_list.accept(self, name)

    def visit_FunctionCallNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionCallNode)

        name = node.identifier.accept(self)

        if name not in self.named_functions:
            return

        params = self.named_functions[name]

        if node.arg_list:
            node.arg_list.accept(self, list(params))

    def visit_VarLoadNode(self, node, byref):
        assert isinstance(node, ast.VarLoadNode)

        if byref:
            return node.var_access
        else:
            return node

    def visit_ArgumentNode(self, node, params=None):
        assert isinstance(node, ast.ArgumentNode)

        if not len(params):
            return

        if params[0] is None:
            byref = True
        else:
            byref = params.pop(0)

        expr = node.expr.accept(self, byref)
        if expr:
            node.expr = expr
