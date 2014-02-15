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
Symbol table for Pascal-86.
'''

import math
import sys


class SymtabException(Exception):
    pass


class Type(object):

    def __init__(self, identifier=None):
        self.identifier = identifier
        self.handle = None

    @property
    def id(self):
        return self.identifier

    def __eq__(self, obj):
        if isinstance(obj, Type):
            return self.id == obj.id

        return False

    def __ne__(self, obj):
        if isinstance(obj, Type):
            return self.id != obj.id

        return True

    def __str__(self):
        return str(self.id)


def _assert_is_type(ty):
    if not isinstance(ty, Type):
        raise SymtabException("Invalid type '%s'", type(ty))


# abstract class
class IntType(Type):

    def __init__(self, lo, hi, width, val=None):
        Type.__init__(self, "p86.int[%d]" % width)

        if width <= 0:
            raise SymtabException('Invalid integer width %d', width)

        self.lo = lo
        self.hi = hi
        self.width = width
        self.value = val

    @property
    def signed(self):
        return self.lo < 0

    @property
    def unsigned(self):
        return self.lo >= 0


class UIntType(IntType):

    def __init__(self, width, val=None):
        lo = 0
        hi = (2 ** width) - 1
        IntType.__init__(self, lo, hi, width, val)
        Type.__init__(self, "p86.uint[%d]" % width)


class SIntType(IntType):

    def __init__(self, width, val=None):
        lo = -(2 ** (width - 1))
        hi = (2 ** (width - 1)) - 1
        IntType.__init__(self, lo, hi, width, val)
        Type.__init__(self, "p86.sint[%d]" % width)


class IntRangeType(IntType):

    def __init__(self, lo, hi, width=None):
        lo = int(lo)
        hi = int(hi)

        lo_ = min(lo, hi)
        hi_ = max(lo, hi)

        if not width:
            num = max(abs(lo_), abs(hi_))
            signed = (lo_ < 0)

            if num > (2 ** 16 - signed) - 1:
                width = 32
            elif num > (2 ** 8 - signed) - 1:
                width = 16
            else:
                width = 8

        IntType.__init__(self, lo_, hi_, width)
        Type.__init__(self, "p86.range[%d..%d]" % (lo_, hi_))


class EnumType(IntType):

    def __init__(self, names, width=None):
        assert len(names) > 0

        self.names = names
        lo = 0
        hi = len(names) - 1

        if not width:
            if hi > (2 ** 16) - 1:
                width = 32
            elif hi > (2 ** 8) - 1:
                width = 16
            else:
                width = 8

        IntType.__init__(self, lo, hi, width)
        Type.__init__(self, "p86.enum[%d..%d]" % (lo, hi))


class BoolType(IntType):

    def __init__(self, val=None):
        lo = 0
        hi = 1
        width = 1
        IntType.__init__(self, lo, hi, width, val)
        Type.__init__(self, "p86.bool")


class CharType(Type):

    def __init__(self, val=None):
        self.hi = 255
        self.lo = 0
        self.width = 8
        self.value = None
        self.signed = False
        self.unsigned = True
        self.value = val

        Type.__init__(self, "p86.char")


class CharRangeType(CharType):

    def __init__(self, lo, hi):
        self.lo = ord(lo)
        self.hi = ord(hi)
        self.width = 8
        self.signed = False
        self.unsigned = True

        Type.__init__(self, "p86.range[%c..%c]" % (self.lo, self.hi))


class RealType(Type):

    def __init__(self, width=32):
        self.width = width

        Type.__init__(self, "p86.real[%d]" % width)


class FloatType(RealType):

    def __init__(self):
        RealType.__init__(self, 32)


class DoubleType(RealType):

    def __init__(self):
        RealType.__init__(self, 64)


class TempRealType(RealType):

    def __init__(self):
        RealType.__init__(self, 80)


class NamedType(Type):

    def __init__(self, name):
        self.name = name
        Type.__init__(self, name)


class DeferredType(NamedType):
    # Type required when named types are used
    # before being defined.
    def __init__(self, name):
        NamedType.__init__(self, name)

    @property
    def id(self):
        return "p86.deferred[%s]" % self.name

class ArrayType(Type):

    def __init__(self, element_ty, range_ty):
        _assert_is_type(element_ty)
        _assert_is_type(range_ty)

        self.element = element_ty
        self.range = range_ty

        Type.__init__(self)

    @property
    def id(self):
        return "p86.array[%d..%d] of %s" % (self.range.lo, self.range.hi,
                                           self.element)

    @property
    def width(self):
        return self.element.width * self.length

    @property
    def length(self):
        return self.range.hi - self.range.lo + 1


class StringType(ArrayType):

    def __init__(self, length):
        element_ty = CharType()
        range_ty = IntRangeType(0, length - 1)

        ArrayType.__init__(self, element_ty, range_ty)


class SetType(Type):

    def __init__(self, element_ty):
        _assert_is_type(element_ty)

        self.element = element_ty
        Type.__init__(self)

    @property
    def id(self):
        return "p86.set of %s" % self.element

    @property
    def width(self):
        return 2 ** self.element.width


class EmptySetType(Type):

    def __init__(self):
        self.value = 0
        Type.__init__(self, "p86.emptyset")


class VoidType(Type):

    def __init__(self):
        Type.__init__(self, "p86.void")


class AnyType(Type):

    def __init__(self):
        Type.__init__(self, "p86.any")


class ReferenceType(Type):

    def __init__(self, referee_ty):
        _assert_is_type(referee_ty)

        self.referee = referee_ty
        Type.__init__(self)

    @property
    def id(self):
        return "p86.reference of %s" % self.referee


class PointerType(Type):

    def __init__(self, pointee_ty):
        _assert_is_type(pointee_ty)

        self.pointee = pointee_ty
        Type.__init__(self)

    @property
    def id(self):
        return "p86.pointer to %s" % self.pointee

    @property
    def width(self):
        return math.log(sys.maxsize, 2) + 1


class FunctionType(NamedType):

    def __init__(self, module, name, ret_ty=VoidType(), scope_level=0):
        _assert_is_type(ret_ty)

        self.ret = ret_ty
        self.params = list()
        self.namespace = module + '.' + name
        self.scope_level = scope_level
        self.scope_hook = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        "p86.function[%s]" % self.namespace


class ParameterType(NamedType):

    def __init__(self, name, ty):
        _assert_is_type(ty)

        self.type = ty

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "p86.param of %s" % self.type

    @property
    def width(self):
        return self.type.width


class RecordType(NamedType):

    def __init__(self, name):
        self.fields = list()
        self.variant = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "p86.record[%s]" % self.name

    @property
    def width(self):
        return sum([x.width for x in self.fields])


class VariantType(NamedType):

    def __init__(self, name):
        self.cases = list()
        self.selector = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "p86.variant[%s]" % self.name

    @property
    def largest(self):
        ty = None

        for case in self.cases:
            if not ty:
                ty = case
            elif ty.width < case.width:
                ty = case

        return ty

    @property
    def width(self):
        return self.largest.width


class FieldType(NamedType):

    def __init__(self, name, ty):
        _assert_is_type(ty)

        self.type = ty
        self.index = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "p86.field[%s]" % self.name

    @property
    def width(self):
        return self.type.width


class ScopeHookType(NamedType):

    def __init__(self, name):
        self.fields = list()

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "p86.scope_hook[%s]" % self.name


class ScopeFieldType(FieldType):

    def __init__(self, name, ty):
        _assert_is_type(ty)

        self.type = ty
        self.index = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "p86.scope_field[%s]" % self.name

    @property
    def width(self):
        return self.type.width


class FileType(Type):

    def __init__(self, component_ty):
        _assert_is_type(component_ty)

        self.component_ty = component_ty
        Type.__init__(self)

    @property
    def id(self):
        return "p86.file of %s" % self.component


def _assert_is_value(value):
    if not isinstance(value, Value):
        raise SymtabException("Invalid value '%s'", value)


class Value(object):
    def __init__(self, handle, ty):
        _assert_is_type(ty)

        self.handle = handle
        self.type = ty

    def __str__(self):
        return str(self.type)


class VariableValue(Value):
    pass


class ConstantValue(Value):
    pass


class FunctionValue(Value):
    pass


class GotoBlock(object):
    def __init__(self):
        self.handle = None
        self.entries = list()


class Symbol(object):

    def __init__(self, name, ty, handle=None):
        _assert_is_type(ty)

        self.name = name
        self.type = ty
        self.handle = handle

    def __str__(self):
        return "%s (%s)" % (self.name, self.type)


class Scope(object):

    def __init__(self):
        self.symbols = dict()
        self.typedefs = dict()
        self.gotos = dict()
        self.functions = dict()

    def dump_symbols(self, prefix=""):
        for name in list(self.symbols.keys()):
            print(("%s: %s" % (prefix, name)))

            sym = self.symbols[name]
            if isinstance(sym, Scope):
                sym.dump_symbols(prefix + "  ")

    def dump_functions(self, prefix=""):
        for name in list(self.functions.keys()):
            print(("%s: %s" % (prefix, name)))

    def dump_typedefs(self, prefix=""):
        for name in list(self.typedefs.keys()):
            print(("%s: %s" % (prefix, name)))

            sym = self.typedefs[name]
            if isinstance(sym, Scope):
                sym.dump_typedefs(prefix + "  ")


class SymbolTable(object):

    def __init__(self):
        self._scopes = list()
        self._lvl = -1  # scope level counter
        self._lbl = 0  # Next label number

    def label(self, s='label'):
        self._lbl += 1
        return "%s_%d" % (s, self._lbl)

    def dump_symbols(self):
        print('---------- SYMBOLS --------------')
        for i, scope in enumerate(self._scopes):
            scope.dump_symbols(" " * i)

    def dump_functions(self):
        print('--------- FUNCTIONS -------------')
        for i, scope in enumerate(self._scopes):
            scope.dump_functions(" " * i)

    def dump_typedefs(self):
        print('--------- TYPEDEFS --------------')
        for i, scope in enumerate(self._scopes):
            scope.dump_typedefs(" " * i)

    def enter_scope(self):
        scope = Scope()
        self._lvl += 1
        self._scopes.append(scope)

    def exit_scope(self):
        self._scopes.pop(self._lvl)
        self._lvl -= 1

    @property
    def symbols(self):
        d = dict()

        for i in range(self._lvl + 1):
            l = list(d.items())
            l += list(self._scopes[i].symbols.items())
            d = dict(l)

        return d.values()

    def install_symbol(self, name, ty, handle=None):
        scope = self._scopes[self._lvl]
        sym = Symbol(name, ty, handle)
        scope.symbols[name] = sym

        return sym

    def find_symbol(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.symbols:
                return scope.symbols[name]

        raise SymtabException("Unknown symbol '%s'" % name)

    def install_const(self, name, ty, handle):
        scope = self._scopes[self._lvl]
        const = ConstantValue(handle, ty)
        scope.symbols[name] = const

        return const

    def install_typedef(self, name, ty):
        scope = self._scopes[self._lvl]
        scope.typedefs[name] = ty

        return ty

    def find_typedef(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.typedefs:
                return scope.typedefs[name]

        raise SymtabException("Unknown typedef '%s'" % name)

    def install_function(self, name, ty, handle=None):
        scope = self._scopes[self._lvl]
        func = FunctionValue(handle, ty)
        scope.functions[name] = func

        return func

    def find_function(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.functions:
                return scope.functions[name]

        raise SymtabException("Unknown function '%s'" % name)

    def install_goto(self, name, goto):
        scope = self._scopes[self._lvl]
        scope.gotos[name] = goto

        return goto

    def find_goto(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.gotos:
                return scope.gotos[name]

        raise SymtabException("Unknown goto label '%s'" % name)
