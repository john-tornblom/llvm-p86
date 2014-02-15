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
LLVM-IR code generation.
'''

import llvm
import llvm.core as lc

from . import ast
from . import symtab
from . import fn
from . import log


def c_int(val, width=32):
    return lc.Constant.int(lc.Type.int(width), val)


def c_char(val):
    return c_int(ord(val), 8)


def c_bool(val):
    return c_int(val, 1)


def c_double(val):
    return lc.Constant.real(lc.Type.double(), val)


def c_float(val):
    # TODO: all reals are doubles
    return lc.Constant.real(lc.Type.double(), val)


def libc_format_string(args):
    fmt = ''

    for arg in args:
        if isinstance(arg.type, symtab.IntType):
            if arg.type.width == 64:
                fmt += '%li'

            if arg.type.width == 32:
                fmt += '%i'

            elif arg.type.width == 16:
                fmt += '%hi'

            elif arg.type.width == 8:
                fmt += '%hhi'

        elif isinstance(arg.type, symtab.CharType):
            fmt += '%c'

        elif isinstance(arg.type, symtab.RealType):
            fmt += '%lf'

        elif isinstance(arg.type, symtab.StringType):
            fmt += '%s'

        elif isinstance(arg.type, symtab.PointerType):
            fmt += '%p'

        elif (isinstance(arg.type, symtab.ArrayType) and
              isinstance(arg.type.element, symtab.CharType)):
            fmt += '%s'

    return fmt


class CodegenException(Exception):
    pass


class CodegenNodeException(CodegenException):

    def __init__(self, node, msg):
        CodegenException.__init__(self)
        self.msg = msg
        self.node = node

    def __str__(self):
        pos = self.node.position
        if not pos:
            pos = '?'

        return str(pos) + ':' + str(self.msg)


class Context(symtab.SymbolTable):

    def __init__(self):
        symtab.SymbolTable.__init__(self)
        self.module = None

    @property
    def builder(self):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if hasattr(scope, 'builder'):
                return scope.builder

    @builder.setter
    def builder(self, val):
        scope = self._scopes[self._lvl]
        scope.builder = val

    @property
    def function(self):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if hasattr(scope, 'function'):
                return scope.function

    @function.setter
    def function(self, val):
        scope = self._scopes[self._lvl]
        scope.function = val

    def cast(self, operand, ty):
        if operand.type == ty:
            return operand

        # print operand, '==>', ty

        # Real --> Int (signed)
        if (isinstance(operand.type, symtab.RealType) and
            isinstance(ty, symtab.IntType) and
            ty.signed):

            return self.fptosi(operand, ty)

        # Real --> Int (unsigned)
        elif (isinstance(operand.type, symtab.RealType) and
            isinstance(ty, symtab.IntType) and
            ty.unsigned):

            return self.fptosi(operand, ty)

        # Real --> Real
        elif (isinstance(operand.type, symtab.RealType) and
            isinstance(ty, symtab.RealType) and
            operand.type.width > ty.width):

            return self.fptrunc(operand, ty)

        # Int --> Int
        elif (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.IntType) and
            operand.type.width > ty.width):

            return self.trunc(operand, ty)

        # Int --> Char
        elif (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.CharType)):

            if operand.type.width > ty.width:
                return self.trunc(operand, ty)
            else:
                return self.zext(operand, ty)

        # Char --> Int
        elif (isinstance(operand.type, symtab.CharType) and
            isinstance(ty, symtab.IntType)):

            return self.zext(operand, ty)

        # Char --> Real
        elif (isinstance(operand.type, symtab.CharType) and
            isinstance(ty, symtab.RealType)):

            return self.uitofp(operand, ty)

        # Reference --> Reference of Any
        elif (isinstance(operand.type, symtab.ReferenceType) and
              isinstance(ty, symtab.ReferenceType) and
              isinstance(ty.referee, symtab.AnyType)):

            return self.bitcast(operand, ty)

        # Pointer --> Pointer to Any
        elif (isinstance(operand.type, symtab.PointerType) and
              isinstance(ty, symtab.PointerType) and
              isinstance(ty.pointee, symtab.AnyType)):

            return self.bitcast(operand, ty)

        # Array --> Reference of Any
        elif (isinstance(operand.type, symtab.ArrayType) and
              isinstance(ty, symtab.ReferenceType) and
              isinstance(ty.referee, symtab.AnyType)):

            return self.bitcast(operand, ty)

        rc = self.coerce(operand, ty)
        if rc:
            return rc

        raise CodegenException("cast from '%s' to '%s'" % (operand.type, ty))

    def coerce(self, operand, ty):
        if operand.type == ty:
            return operand

        # print operand, '-->', ty

        # Int (signed) --> Real
        if (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.RealType) and
            operand.type.signed):

            return self.sitofp(operand, ty)

        # Int (unsigned) --> Real
        elif (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.RealType) and
            operand.type.unsigned):

            return self.sitofp(operand, ty)

        # Real --> Real
        elif (isinstance(operand.type, symtab.RealType) and
            isinstance(ty, symtab.RealType) and
            operand.type.width <= ty.width):

            return self.sitofp(operand, ty)

        # Int (signed) --> Int (signed)
        elif (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.IntType) and
            operand.type.width <= ty.width and
            operand.type.signed and ty.signed):

            return self.sext(operand, ty)

        # Int (unsigned) --> Int (signed)
        elif (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.IntType) and
            operand.type.width <= ty.width and
            operand.type.unsigned and ty.signed):

            return self.zext(operand, ty)

        # Int (signed) --> Int (unsigned)
        elif (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.IntType) and
            operand.type.width <= ty.width and
            operand.type.signed and ty.unsigned):

            return self.sext(operand, ty)

        # Int (unsigned) --> Int (unsigned)
        elif (isinstance(operand.type, symtab.IntType) and
            isinstance(ty, symtab.IntType) and
            operand.type.width <= ty.width and
            operand.type.unsigned and ty.unsigned):

            return self.zext(operand, ty)

        # EmptySet --> Set
        elif (isinstance(operand.type, symtab.EmptySetType) and
              isinstance(ty, symtab.SetType)):

            return self.zext(operand, ty)

        # Int --> Set (e.g. 3 in [1, 2, 3])
        elif (isinstance(operand.type, symtab.IntType) and
              isinstance(ty, symtab.SetType) and
              operand.type.width <= ty.width):

            return self.zext(operand, ty)

        # Set --> Set
        elif (isinstance(operand.type, symtab.SetType) and
              isinstance(ty, symtab.SetType) and
              ty.element.lo <= operand.type.element.lo and
              ty.element.hi >= operand.type.element.hi):

            return self.zext(operand, ty)

        # Pointer of Any (Null) --> Pointer
        elif (isinstance(operand.type, symtab.PointerType) and
              isinstance(ty, symtab.PointerType) and
              isinstance(operand.type.pointee, symtab.AnyType)):

            type_ = self.typegen(ty)
            handle = lc.Constant.null(type_)
            return symtab.ConstantValue(handle, ty)

        # Array --> String (within range, same type width)
        elif (isinstance(operand.type, symtab.StringType) and
              isinstance(ty, symtab.ArrayType) and
              operand.type.element.width == ty.element.width and
              operand.type.length <= ty.length):

            # preserve the String type
            ty = symtab.StringType(ty.length)
            return symtab.ConstantValue(operand.handle, ty)

        # Array --> Array (within range, same type width)
        elif (isinstance(operand.type, symtab.ArrayType) and
              isinstance(ty, symtab.ArrayType) and
              operand.type.element.width == ty.element.width and
              operand.type.length <= ty.length):

            return symtab.ConstantValue(operand.handle, ty)

        # log.w('codegen', "Unknown coerce from '%s' to '%s'", operand.type, ty)

    def typegen(self, ty):
        if ty.handle:
            return ty.handle

        ty.handle = self._typegen(ty)
        return ty.handle

    def _typegen(self, ty):

        if isinstance(ty, symtab.IntType):
            return lc.Type.int(ty.width)

        elif isinstance(ty, symtab.CharType):
            return lc.Type.int(8)

        elif isinstance(ty, symtab.FloatType):
            return lc.Type.double()

        elif isinstance(ty, symtab.DoubleType):
            return lc.Type.double()

        elif isinstance(ty, symtab.TempRealType):
            return lc.Type.double()

        elif isinstance(ty, symtab.ArrayType):
            el_type = self.typegen(ty.element)
            length = ty.range.hi - ty.range.lo + 1
            return lc.Type.array(el_type, length)

        elif isinstance(ty, symtab.RecordType):
            ty.handle = lc.Type.opaque(ty.name)
            field_types = [self.typegen(x.type) for x in ty.fields]

            if ty.variant:
                selector = ty.variant.selector
                selector = self.typegen(selector.type)
                field_types.append(selector)

                largest = ty.variant.largest
                if largest:
                    largest = self.typegen(largest)
                    field_types.append(largest)

            ty.handle.set_body(field_types)
            return ty.handle

        elif isinstance(ty, symtab.FieldType):
            return self.typegen(ty.type)

        elif isinstance(ty, symtab.SetType):
            return lc.Type.int(ty.width)

        elif isinstance(ty, symtab.EmptySetType):
            return lc.Type.int(1)

        elif isinstance(ty, symtab.FunctionType):
            param_types = [self.typegen(x.type) for x in ty.params]
            ret_type = self.typegen(ty.ret)
            return lc.Type.function(ret_type, param_types)

        elif isinstance(ty, symtab.VoidType):
            return lc.Type.void()

        elif isinstance(ty, symtab.ReferenceType):
            ref_type = self.typegen(ty.referee)
            return lc.Type.pointer(ref_type)

        elif isinstance(ty, symtab.PointerType):
            pointer_type = self.typegen(ty.pointee)
            return lc.Type.pointer(pointer_type)

        elif isinstance(ty, symtab.ScopeHookType):
            field_types = [self.typegen(x.type) for x in ty.fields]
            field_types = [lc.Type.pointer(x) for x in field_types]
            return lc.Type.struct(field_types, ty.name + '.scope')

        elif isinstance(ty, symtab.AnyType):
            # llvm doesn't support void*. Instead, i8* should be used
            return lc.Type.int(8)

        raise CodegenException("unknown type '%s'" % type(ty))

    def c_string(self, val, pointer=False):
        if pointer:
            ty = symtab.CharType()
        else:
            length = len(val)
            ty = symtab.StringType(length + 1)

        type_ = self.typegen(ty)

        value = lc.GlobalVariable.new(self.module, type_, "conststr")
        value.initializer = lc.Constant.stringz(val)
        value.linkage = lc.LINKAGE_INTERNAL
        value.global_constant = True

        return symtab.ConstantValue(value, ty)

    def translate_call(self, name, args):
        if name == 'writeln' or name == 'write':
            func_value = fn.f_printf(self.module)
            func_type = fn.translate_function(func_value)
            func = symtab.FunctionValue(func_value, func_type)

            # printf doesn't support boolean or floats
            # instead, we upcast them before printing to stdout
            for i in range(len(args)):
                if isinstance(args[i].type, symtab.BoolType):
                    ty = symtab.UIntType(16)
                    args[i] = self.cast(args[i], ty)
                elif isinstance(args[i].type, symtab.RealType):
                    ty = symtab.DoubleType()
                    args[i] = self.cast(args[i], ty)

            fmt = libc_format_string(args)
            if name == 'writeln':
                fmt += '\n'

            arg = self.c_string(fmt)
            args.insert(0, arg)

            # cast char array to char pointer
            for i in range(len(args)):
                if isinstance(args[i].type, symtab.StringType):
                    type_ = func_value.args[0].type  # char*
                    value = args[i].handle
                    value = self.builder.bitcast(value, type_)
                    args[i] = symtab.ConstantValue(value, args[i].type)

            return func, args

        elif name == 'halt':
            handle = fn.f_exit(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            # halt is a variadic function
            if len(args) == 0:
                ty = symtab.SIntType(32)
                type_ = self.typegen(ty)
                handle = lc.Constant.int(type_, 0)

                arg = symtab.ConstantValue(handle, ty)
                args.insert(0, arg)
            else:
                # typesys allow any type, cast the argument
                args[0] = self.cast(args[0], ty.params[0].type)

            return func, args

        elif name == 'paramstr':
            handle = fn.f_paramstr(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'paramcount':
            handle = fn.f_paramcount(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'read' or name == 'readln':
            func_value = fn.f_scanf(self.module)
            func_type = fn.translate_function(func_value)
            func = symtab.FunctionValue(func_value, func_type)

            fmt = libc_format_string(args)

            # TODO: scanf doesn't support booleans etc
            arg = self.c_string(fmt)
            args.insert(0, arg)

            # cast char array to char pointer
            for i in range(len(args)):
                if isinstance(args[i].type, symtab.StringType):
                    type_ = func_value.args[0].type  # char*
                    value = args[i].handle
                    value = self.builder.bitcast(value, type_)
                    args[i] = symtab.ConstantValue(value, args[i].type)

                elif (isinstance(args[i].type, symtab.IntType) or
                      isinstance(args[i].type, symtab.RealType)):
                    value = args[i].handle
                    ty = symtab.ReferenceType(args[i].type)
                    args[i] = symtab.ConstantValue(value, ty)

            return func, args

        elif name == 'sqr':
            handle = c_double(2)
            ty = symtab.DoubleType()
            arg = symtab.ConstantValue(handle, ty)

            handle = fn.f_pow(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            args.append(arg)

            return func, args

        elif name == 'sqrt':
            handle = fn.f_sqrt(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'round':
            handle = fn.f_round(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'lround':
            handle = fn.f_lround(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'trunc':
            handle = fn.f_trunc(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'ltrunc':
            handle = fn.f_ltrunc(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'ord' or name == 'wrd' or name == 'lord':
            if isinstance(args[0].type, symtab.StringType):
                handle = fn.f_atoi(self.module)
            else:
                handle = fn.f_ord(self.module)

            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            # typesys allow any type, cast the argument
            args[0] = self.cast(args[0], ty.params[0].type)

            return func, args

        elif name == 'chr':
            handle = fn.f_chr(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'succ':
            handle = fn.f_succ(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            # typesys allow any type, cast the argument
            args[0] = self.cast(args[0], ty.params[0].type)

            return func, args

        elif name == 'pred':
            handle = fn.f_pred(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            # typesys allow any type, cast the argument
            args[0] = self.cast(args[0], ty.params[0].type)

            return func, args

        elif name == 'odd':
            handle = fn.f_odd(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'abs':
            handle = fn.f_fabs(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'sin':
            handle = fn.f_sin(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'cos':
            handle = fn.f_cos(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'tan':
            handle = fn.f_tan(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'arcsin':
            handle = fn.f_arcsin(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'arccos':
            handle = fn.f_arccos(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'arctan':
            handle = fn.f_arctan(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'exp':
            handle = fn.f_exp(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'ln':
            handle = fn.f_ln(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'size':
            handle = fn.f_size(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            # f_size is just a dummy function that returns
            # the argument. The size is calculated here.
            arg_type = self.typegen(args[0].type)
            size_handle = lc.Constant.sizeof(arg_type)
            size_ty = symtab.UIntType(32)

            args[0] = symtab.ConstantValue(size_handle, size_ty)
            return func, args

        elif name == 'outbyt' or name == 'inbyt':
            handle = fn.f_outbyt(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            args[1] = symtab.ConstantValue(c_int(0, 8), symtab.UIntType(8))

            return func, args

        elif name == 'outwrd' or name == 'inwrd':
            handle = fn.f_outwrd(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            args[1] = symtab.ConstantValue(c_int(0, 16), symtab.UIntType(16))

            return func, args

        elif name == 'setinterrupt':
            handle = fn.f_setinterrupt(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            args = [args[0]]  # drop function
            return func, args

        elif name == 'enableinterrupts':
            handle = fn.f_enableinterrupts(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'disableinterrupts':
            handle = fn.f_disableinterrupts(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'setmutation':
            handle = fn.f_set_mutation(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'setmutationid':
            handle = fn.f_set_mutation_id(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'getmutationid':
            handle = fn.f_get_mutation_id(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'getmutationmod':
            handle = fn.f_get_mutation_mod(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'getmutationcount':
            handle = fn.f_get_mutation_count(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'new':
            handle = fn.f_new(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            length = c_int(int(args[0].type.referee.pointee.width / 8))
            length = symtab.ConstantValue(length, symtab.UIntType(32))
            args.append(length)

            type_ = handle.args[0].type
            ptr = self.builder.bitcast(args[0].handle, type_)
            args[0] = symtab.ConstantValue(ptr, args[0].type)

            return func, args

        elif name == 'dispose':
            handle = fn.f_dispose(self.module)
            ty = fn.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            type_ = handle.args[0].type
            ptr = self.builder.bitcast(args[0].handle, type_)
            args[0] = symtab.ConstantValue(ptr, args[0].type)

            return func, args

        raise CodegenException("call to unknown function '%s'" % name)

    def scope_hook(self, ty):
        assert isinstance(ty, symtab.ScopeHookType)

        type_ = self.typegen(ty)
        scope = self.builder.alloca(type_, name='call_hook')

        for field in ty.fields:
            indices = [c_int(0), c_int(field.index)]
            var = self.builder.gep(scope, indices)
            sym = self.find_symbol(field.name)
            self.builder.store(sym.handle, var)

        return scope

    def call(self, func, args=[]):
        assert isinstance(func, symtab.FunctionValue)

        args = [x.handle for x in args]

        if func.type.scope_hook:
            param_ty = func.type.params[-1]
            ref_ty = param_ty.type
            hook_ty = ref_ty.referee
            hook_val = self.scope_hook(hook_ty)

            ref_val = self.builder.gep(hook_val, [c_int(0)])
            args.append(ref_val)

        value = self.builder.call(func.handle, args)

        return symtab.ConstantValue(value, func.type.ret)

    def add(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            if not self.builder:
                value = left.handle.fadd(right.handle)
            else:
                value = self.builder.fadd(left.handle, right.handle)

        elif isinstance(left.type, symtab.SetType):
            if not self.builder:
                value = left.handle.or_(right.handle)
            else:
                value = self.builder.or_(left.handle, right.handle)

        else:
            if not self.builder:
                value = left.handle.add(right.handle)
            else:
                value = self.builder.add(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def sub(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            if not self.builder:
                value = left.handle.fsub(left.handle, right.handle)
            else:
                value = self.builder.fsub(left.handle, right.handle)

        elif isinstance(left.type, symtab.SetType):
            if not self.builder:
                value = right.handle.not_()
                value = left.handle.and_(value)
            else:
                value = self.builder.not_(right.handle)
                value = self.builder.and_(left.handle, value)

        else:
            if not self.builder:
                value = left.handle.sub(right.handle)
            else:
                value = self.builder.sub(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def mul(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            if not self.builder:
                value = left.handle.fmul(right.handle)
            else:
                value = self.builder.fmul(left.handle, right.handle)

        elif isinstance(left.type, symtab.SetType):
            if not self.builder:
                value = left.handle.and_(right.handle)
            else:
                value = self.builder.and_(left.handle, right.handle)

        else:
            if not self.builder:
                value = left.handle.mul(right.handle)
            else:
                value = self.builder.mul(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def mod(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            if not self.builder:
                value = left.handle.frem(right.handle)
            else:
                value = self.builder.frem(left.handle, right.handle)

        elif isinstance(left.type, symtab.UIntType):
            if not self.builder:
                value = left.handle.urem(right.handle)
            else:
                value = self.builder.urem(left.handle, right.handle)

        else:
            if not self.builder:
                value = left.handle.srem(right.handle)
            else:
                value = self.builder.srem(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def div(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            if not self.builder:
                value = left.handle.fdiv(right.handle)
            else:
                value = self.builder.fdiv(left.handle, right.handle)
        else:

            if not self.builder:
                value = left.handle.sdiv(right.handle)
            else:
                value = self.builder.sdiv(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def cmp_eq(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            value = self.builder.fcmp(lc.FCMP_OEQ, left.handle, right.handle)

        else:
            value = self.builder.icmp(lc.ICMP_EQ, left.handle, right.handle)

        return symtab.ConstantValue(value, symtab.BoolType())

    def cmp_neq(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            value = self.builder.fcmp(lc.FCMP_ONE, left.handle, right.handle)

        else:
            value = self.builder.icmp(lc.ICMP_NE, left.handle, right.handle)

        return symtab.ConstantValue(value, symtab.BoolType())

    def cmp_gt(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            value = self.builder.fcmp(lc.FCMP_OGT, left.handle, right.handle)

        elif (isinstance(left.type, symtab.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp(lc.ICMP_SGT, left.handle, right.handle)

        else:
            value = self.builder.icmp(lc.ICMP_UGT, left.handle, right.handle)

        return symtab.ConstantValue(value, symtab.BoolType())

    def cmp_ge(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            value = self.builder.fcmp(lc.FCMP_OGE, left.handle, right.handle)

        elif (isinstance(left.type, symtab.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp(lc.ICMP_SGE, left.handle, right.handle)

        else:
            value = self.builder.icmp(lc.ICMP_UGE, left.handle, right.handle)

        return symtab.ConstantValue(value, symtab.BoolType())

    def cmp_lt(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            value = self.builder.fcmp(lc.FCMP_OLT, left.handle, right.handle)

        elif (isinstance(left.type, symtab.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp(lc.ICMP_SLT, left.handle, right.handle)

        else:
            value = self.builder.icmp(lc.ICMP_ULT, left.handle, right.handle)

        return symtab.ConstantValue(value, symtab.BoolType())

    def cmp_le(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, symtab.RealType):
            value = self.builder.fcmp(lc.FCMP_OLE, left.handle, right.handle)

        elif (isinstance(left.type, symtab.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp(lc.ICMP_SLE, left.handle, right.handle)

        else:
            value = self.builder.icmp(lc.ICMP_ULE, left.handle, right.handle)

        return symtab.ConstantValue(value, symtab.BoolType())

    def and_(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        value = self.builder.and_(left.handle, right.handle)
        return symtab.ConstantValue(value, symtab.BoolType())

    def or_(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        value = self.builder.or_(left.handle, right.handle)
        return symtab.ConstantValue(value, symtab.BoolType())

    def in_(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        type_ = self.typegen(right.type)
        value = self.builder.zext(left.handle, type_)
        value = self.builder.shl(c_int(1, type_.width), value)

        value = self.builder.and_(value, right.handle)
        value = self.builder.icmp(lc.ICMP_NE, c_int(0, type_.width), value)

        return symtab.ConstantValue(value, symtab.BoolType())

    def not_(self, operand):
        assert isinstance(operand, symtab.Value)

        value = self.builder.not_(operand.handle)
        return symtab.ConstantValue(value, operand.type)

    def neg(self, operand):
        assert isinstance(operand, symtab.Value)

        if isinstance(operand.type, symtab.IntType):
            zero = c_int(0, operand.type.width)

            if not self.builder:
                value = zero.sub(operand.handle)
            else:
                value = self.builder.sub(zero, operand.handle)

            return symtab.ConstantValue(value, operand.type)

        elif isinstance(operand.type, symtab.DoubleType):
            zero = c_double(0)

            if not self.builder:
                value = zero.fsub(operand.handle)
            else:
                value = self.builder.fsub(zero, operand.handle)

            return symtab.ConstantValue(value, operand.type)

        elif isinstance(operand.type, symtab.FloatType):
            zero = c_float(0)

            if not self.builder:
                value = zero.fsub(operand.handle)
            else:
                value = self.builder.fsub(zero, operand.handle)

            return symtab.ConstantValue(value, operand.type)

    def fptosi(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.fptosi(type_)
        else:
            handle = self.builder.fptosi(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def fptoui(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.fptoui(type_)
        else:
            handle = self.builder.fptoui(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def fptrunc(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.fptrunc(type_)
        else:
            handle = self.builder.fptrunc(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def trunc(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.trunc(type_)
        else:
            handle = self.builder.trunc(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def sitofp(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)

        if not self.builder:
            handle = operand.handle.sitofp(type_)
        else:
            handle = self.builder.sitofp(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def uitofp(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)

        if not self.builder:
            handle = operand.handle.uitofp(type_)
        else:
            handle = self.builder.uitofp(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def fpext(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if operand.handle.type == type_:
            return symtab.ConstantValue(operand.handle, ty)

        if not self.builder:
            handle = operand.handle.fpext(type_)
        else:
            handle = self.builder.fpext(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def sext(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if operand.handle.type.width == type_.width:
            return symtab.ConstantValue(operand.handle, ty)

        if not self.builder:
            handle = operand.handle.sext(type_)
        else:
            handle = self.builder.sext(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def zext(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if operand.handle.type.width == type_.width:
                return symtab.ConstantValue(operand.handle, ty)

        if not self.builder:
            handle = operand.handle.zext(type_)
        else:
            handle = self.builder.zext(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def bitcast(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, symtab.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.bitcast(type_)
        else:
            handle = self.builder.bitcast(operand.handle, type_)

        return symtab.ConstantValue(handle, operand.type)


class CodegenVisitor(ast.DefaultP86Visitor):

    def __init__(self, mutants):
        self.mutants = mutants
        self.ctx = Context()
        self.ctx.enter_scope()
        self.func_scope_level = 0

        self.ctx.module = lc.Module.new('P86.noname')

        self.ctx.install_typedef('boolean' , symtab.BoolType())
        self.ctx.install_typedef('char'    , symtab.CharType())
        self.ctx.install_typedef('integer' , symtab.SIntType(16))
        self.ctx.install_typedef('word'    , symtab.UIntType(16))
        self.ctx.install_typedef('longint' , symtab.SIntType(32))
        self.ctx.install_typedef('longreal', symtab.DoubleType())
        self.ctx.install_typedef('real'    , symtab.FloatType())
        self.ctx.install_typedef('tempreal', symtab.TempRealType())

        self.ctx.install_const('cr'        , symtab.CharType()  , c_char('\r'))
        self.ctx.install_const('false'     , symtab.BoolType()  , c_bool(False))
        self.ctx.install_const('lf'        , symtab.CharType()  , c_char('\n'))
        self.ctx.install_const('maxint'    , symtab.SIntType(16), c_int((2 ** 15) - 1, 16))
        self.ctx.install_const('maxlongint', symtab.SIntType(32), c_int((2 ** 31) - 1, 32))
        self.ctx.install_const('maxword'   , symtab.UIntType(16), c_int((2 ** 16) - 1, 16))
        self.ctx.install_const('true'      , symtab.BoolType()  , c_bool(True))

    def visit(self, node, arg=None):
        try:
            # print node, node.position
            return ast.DefaultP86Visitor.visit(self, node, arg)
        except CodegenException as e:
            log.e('codegen', str(e))
        except symtab.SymtabException as e:
            log.e('codegen', str(e))
        except llvm.LLVMException as e:
            log.e('codegen', str(e))

######################
#    Scope stuff     #
######################

    def visit_ModuleNode(self, node, arg=None):
        assert isinstance(node, ast.ModuleNode)

        self.ctx.module.id = node.identifier.accept(self)

        if node.interface:
            node.interface.accept(self)

        if node.entry_point:
            node.entry_point.accept(self)

    def visit_ProgramNode(self, node, arg=None):
        assert isinstance(node, ast.ProgramNode)

        name = node.identifier.accept(self)
        if name:
            self.ctx.module.id = name

        fn.define_libp86(self.ctx)
        fn.define_mutation(self.ctx)
        fn.define_ctor(self.ctx, self.mutants)

        self.ctx.enter_scope()

        func = fn.f_main(self.ctx.module)
        block = func.append_basic_block("entry")
        self.ctx.builder = lc.Builder.new(block)
        self.ctx.function = func

        # copy the arguments to global variables so that the builtin
        # functions P86.paramcount() and P86.paramstr() work
        argv_value = self.ctx.module.get_global_variable_named("P86.argv")
        argc_value = self.ctx.module.get_global_variable_named("P86.argc")
        self.ctx.builder.store(func.args[0], argc_value)
        self.ctx.builder.store(func.args[1], argv_value)

        if node.block:
            node.block.accept(self)

        self.ctx.builder.ret_void()

        self.ctx.exit_scope()

    def visit_NonMainNode(self, node, arg=None):
        assert isinstance(node, ast.NonMainNode)

        self.ctx.module.id = node.identifier.accept(self)
        fn.define_ctor(self.ctx, self.mutants)

        if node.const_list:
            node.const_list.accept(self)

        if node.type_list:
            node.type_list.accept(self)

        if node.var_list:
            node.var_list.accept(self)

        if node.func:
            node.func.accept(self)

    def visit_FunctionHeadNode(self, node, arg=None):
        assert (isinstance(node, ast.FunctionHeadNode) or
                isinstance(node, ast.ProcedureHeadNode))

        ty = node.type
        if ty.scope_level > 0:
            # Nested function require a hook to its parent scope
            # we append them at the end of the parameter list
            scope_ty = symtab.ScopeHookType(ty.name)
            index = 0
            for sym in self.ctx.symbols:
                # Ignore constants
                if isinstance(sym.handle, lc.Constant):
                    continue

                # when several scopes are nested, we just point
                # at the same place
                if isinstance(sym.type, symtab.ScopeFieldType):
                    sym_ty = sym.type.type
                else:
                    sym_ty = sym.type

                field = symtab.ScopeFieldType(sym.name, sym_ty)
                field.index = index
                scope_ty.fields.append(field)

                index += 1

            if index > 0:
                scope_ty = symtab.ReferenceType(scope_ty)
                param_ty = symtab.ParameterType('hook', scope_ty)
                ty.params.append(param_ty)
                ty.scope_hook = True

        try:
            handle_ = lc.Function.get(self.ctx.module, ty.namespace)
        except:
            type_ = self.ctx.typegen(ty)
            handle_ = lc.Function.new(self.ctx.module, type_, ty.namespace)
            handle_.linkage = lc.LINKAGE_PRIVATE

        return self.ctx.install_function(ty.name, ty, handle_)

    def visit_ProcedureHeadNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureHeadNode)

        return self.visit_FunctionHeadNode(node, arg)

    def visit_FunctionNode(self, node, arg=None):
        assert (isinstance(node, ast.FunctionNode) or
                isinstance(node, ast.ProcedureNode))

        func = node.header.accept(self)

        self.func_scope_level += 1
        self.ctx.enter_scope()

        self.ctx.function = func.handle
        self.ctx.builder = lc.Builder.new(
                              func.handle.append_basic_block("func.entry"))

        # allocate arguments
        for arg, param in zip(self.ctx.function.args, func.type.params):
            handle = self.ctx.builder.alloca(arg.type, name=param.name)
            self.ctx.builder.store(arg, handle)

            param_ty = param.type
            if isinstance(param_ty, symtab.ReferenceType):
                handle = self.ctx.builder.load(handle)
                param_ty = param_ty.referee

            # install (and load) variables declared on a parent stack
            if isinstance(param_ty, symtab.ScopeHookType):
                for field in param_ty.fields:
                    indices = [c_int(0), c_int(field.index)]
                    field_handle = self.ctx.builder.gep(handle, indices)
                    field_handle = self.ctx.builder.load(
                                        field_handle, field.name)
                    self.ctx.install_symbol(field.name, field, field_handle)

            else:
                self.ctx.install_symbol(param.name, param_ty, handle)

        # generate return value
        if not isinstance(func.type.ret, symtab.VoidType):
            type_ = self.ctx.typegen(func.type.ret)
            value = self.ctx.builder.alloca(type_, name=func.type.name)
            self.ctx.install_symbol(func.type.name, func.type.ret, value)

        if node.block:
            node.block.accept(self)

        if not isinstance(func.type.ret, symtab.VoidType):
            ret = self.ctx.builder.load(value)
            self.ctx.builder.ret(ret)
        else:
            self.ctx.builder.ret_void()

        self.ctx.exit_scope()
        self.func_scope_level -= 1

    def visit_ProcedureNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureNode)

        return self.visit_FunctionNode(node, arg)

    def visit_PublicSectionNode(self, node, arg=None):
        assert isinstance(node, ast.PublicSectionNode)

        name = node.identifier.accept(self)
        external = (self.ctx.module.id != name)

        if node.section:
            node.section.accept(self, external)

    def visit_PublicFunctionNode(self, node, external):
        assert (isinstance(node, ast.PublicFunctionNode) or
                isinstance(node, ast.PublicProcedureNode))

        ty = node.heading.type
        type_ = self.ctx.typegen(ty)
        handle = lc.Function.get_or_insert(self.ctx.module, type_,
                                           ty.namespace)
        self.ctx.install_function(ty.name, ty, handle)

    def visit_PublicProcedureNode(self, node, external):
        assert isinstance(node, ast.PublicProcedureNode)

        return self.visit_PublicFunctionNode(node, external)

    def visit_WithNode(self, node, arg=None):
        assert isinstance(node, ast.WithNode)

        self.ctx.enter_scope()

        for rec in node.rec_var_list.accept(self):
            ty = rec.type

            if isinstance(ty, symtab.ReferenceType):
                ty = ty.referee

            if isinstance(ty, symtab.ScopeFieldType):
                ty = ty.type

            # install regular fields in the symbol table
            offset = 0
            for field in ty.fields:
                indices = [c_int(0), c_int(offset)]
                handle = self.ctx.builder.gep(rec.handle, indices)
                self.ctx.install_symbol(field.name, field.type, handle)

                offset += 1

            if ty.variant is None:
                continue

            # install the selector in the symbol table
            # I'm not really sure what it is used for,
            # but it can hold values
            if ty.variant.selector:
                selector = ty.variant.selector
                indices = [c_int(0), c_int(offset)]
                handle = self.ctx.builder.gep(rec.handle, indices)
                self.ctx.install_symbol(selector.name, selector.type)

                offset += 1

            # install the variants in the symbol table
            # each variant case is a record on its own
            for case in ty.variant.cases:
                case_offset = 0
                for field in case.fields:
                    indices = [c_int(0), c_int(offset)]
                    handle = self.ctx.builder.gep(rec.handle, indices)

                    type_ = self.ctx.typegen(case)
                    handle = self.ctx.builder.bitcast(handle,
                                                      lc.Type.pointer(type_))

                    indices = [c_int(0), c_int(case_offset)]
                    handle = self.ctx.builder.gep(handle, indices)

                    self.ctx.install_symbol(field.name, field.type, handle)

                    case_offset += 1

        if node.statement_list:
            node.statement_list.accept(self)

        self.ctx.exit_scope()

######################
#    Declarations    #
######################

    def visit_LabelDeclNode(self, node, arg=None):
        assert isinstance(node, ast.LabelDeclNode)

        for lbl in node.label_list.accept(self, arg):
            block = symtab.GotoBlock()
            self.ctx.install_goto(lbl, block)

    def visit_ConstDeclNode(self, node, arg=None):
        assert isinstance(node, ast.ConstDeclNode)

        name = node.identifier.accept(self)
        expr = node.expr.accept(self)

        self.ctx.install_const(name, node.type, expr.handle)

    def visit_TypeDeclNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclNode)

        name = node.identifier.accept(self)
        node.type_denoter.accept(self)  # will install enums

        self.ctx.install_typedef(name, node.type)

    def visit_EnumTypeNode(self, node, arg=None):
        assert isinstance(node, ast.EnumTypeNode)

        names = node.identifier_list.accept(self)
        type_ = self.ctx.typegen(node.type)

        for i, name in enumerate(names):
            value = lc.Constant.int(type_, i)
            self.ctx.install_const(name, node.type, value)

    def visit_VarDeclNode(self, node, external=None):
        assert isinstance(node, ast.VarDeclNode)

        names = node.identifier_list.accept(self)
        node.type_denoter.accept(self)  # installs constants from sets etc
        type_ = self.ctx.typegen(node.type)

        for name in names:
            if self.func_scope_level <= 0:
                value = lc.GlobalVariable.new(self.ctx.module, type_, name)
                if external:
                    value.linkage = lc.LINKAGE_EXTERNAL
                elif external is None:
                    value.linkage = lc.LINKAGE_PRIVATE
                    value.initializer = lc.Constant.undef(type_)
                else:
                    value.linkage = lc.LINKAGE_EXTERNAL
                    value.initializer = lc.Constant.undef(type_)
            else:
                value = self.ctx.builder.alloca(type_, name=name)

            self.ctx.install_symbol(name, node.type, value)

######################
#     Branching      #
######################

    def visit_IfNode(self, node, arg=None):
        assert isinstance(node, ast.IfNode)

        bb_true = self.ctx.function.append_basic_block('if.true')
        bb_endif = self.ctx.function.append_basic_block('if.end')

        if node.iffalse:
            bb_false = self.ctx.function.append_basic_block('if.false')
        else:
            bb_false = bb_endif

        cond = node.expr.accept(self)

        branch = self.ctx.builder.cbranch(cond.handle, bb_true, bb_false)

        if hasattr(node, 'branch_prediction'):
            mds = lc.MetaDataString.get(self.ctx.module, 'branch_weights')

            if node.branch_prediction is True:
                true = c_int(len(self.mutants))
                false = c_int(1)
            elif node.branch_prediction is False:
                true = c_int(1)
                false = c_int(len(self.mutants))
            else:
                true = c_int(1)
                false = c_int(1)

            md = lc.MetaData.get(self.ctx.module, [mds, true, false])
            branch.set_metadata('prof', md)

        self.ctx.builder.position_at_end(bb_true)
        if node.iftrue:
            node.iftrue.accept(self)

        self.ctx.builder.branch(bb_endif)

        if node.iffalse:
            self.ctx.builder.position_at_end(bb_false)
            node.iffalse.accept(self)
            self.ctx.builder.branch(bb_endif)

        self.ctx.builder.position_at_end(bb_endif)

    def visit_WhileNode(self, node, arg=None):
        assert isinstance(node, ast.WhileNode)

        bb_cond = self.ctx.function.append_basic_block('while.cond')
        bb_body = self.ctx.function.append_basic_block('while.body')
        bb_exit = self.ctx.function.append_basic_block('while.exit')

        # cond block
        self.ctx.builder.branch(bb_cond)
        self.ctx.builder.position_at_end(bb_cond)
        cond = node.cond.accept(self)
        self.ctx.builder.cbranch(cond.handle, bb_body, bb_exit)

        # body block
        self.ctx.builder.position_at_end(bb_body)
        node.body.accept(self)
        self.ctx.builder.branch(bb_cond)

        # exit block
        self.ctx.builder.position_at_end(bb_exit)

    def visit_RepeatNode(self, node, arg=None):
        assert isinstance(node, ast.RepeatNode)

        bb_body = self.ctx.function.append_basic_block('repeat.body')
        bb_cond = self.ctx.function.append_basic_block('repeat.cond')
        bb_exit = self.ctx.function.append_basic_block('repeat.exit')

        # body block
        self.ctx.builder.branch(bb_body)
        self.ctx.builder.position_at_end(bb_body)
        node.body.accept(self)
        self.ctx.builder.branch(bb_cond)

        # cond block
        self.ctx.builder.position_at_end(bb_cond)
        cond = node.cond.accept(self)
        self.ctx.builder.cbranch(cond.handle, bb_exit, bb_body)

        # exit block
        self.ctx.builder.position_at_end(bb_exit)

    def visit_ForNode(self, node, arg=None):
        assert isinstance(node, ast.ForNode)

        bb_cond = self.ctx.function.append_basic_block('for.cond')
        bb_incr = self.ctx.function.append_basic_block('for.incr')
        bb_body = self.ctx.function.append_basic_block('for.body')
        bb_exit = self.ctx.function.append_basic_block('for.exit')

        # generate initializer
        name = node.var.accept(self)
        var = self.ctx.find_symbol(name)
        value = node.value_start.accept(self)

        self.ctx.builder.store(value.handle, var.handle)
        self.ctx.builder.branch(bb_cond)

        # generate condition
        self.ctx.builder.position_at_end(bb_cond)
        handle = self.ctx.builder.load(var.handle)
        var_value = symtab.ConstantValue(handle, var.type)
        value = node.value_end.accept(self)

        if node.direction == 'to':
            cond = self.ctx.cmp_le(var_value, value)
        elif node.direction == 'downto':
            cond = self.ctx.cmp_ge(var_value, value)
        else:
            raise CodegenNodeException(node, "unknown loop direction '%s'" %
                                             node.direction)

        self.ctx.builder.cbranch(cond.handle, bb_body, bb_exit)

        # generate increment
        self.ctx.builder.position_at_end(bb_incr)

        handle = self.ctx.builder.load(var.handle)
        var_value = symtab.ConstantValue(handle, var.type)
        one = symtab.ConstantValue(c_bool(1), symtab.BoolType())
        one = self.ctx.cast(one, var.type)

        if node.direction == 'to':
            var_value = self.ctx.add(var_value, one)
        elif node.direction == 'downto':
            var_value = self.ctx.sub(var_value, one)
        else:
            raise CodegenNodeException(node, "unknown loop direction '%s'" %
                                             node.direction)

        self.ctx.builder.store(var_value.handle, var.handle)
        self.ctx.builder.branch(bb_cond)

        # generate body
        self.ctx.builder.position_at_end(bb_body)
        node.body.accept(self)
        self.ctx.builder.branch(bb_incr)

        # move to exit block
        self.ctx.builder.position_at_end(bb_exit)

    def visit_CaseStatementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseStatementNode)

        bb_switch = self.ctx.function.append_basic_block('switch.entry')

        value = node.case_index.accept(self)

        self.ctx.builder.branch(bb_switch)
        self.ctx.builder.position_at_end(bb_switch)

        if node.case_list_element_list:
            bb_cases = node.case_list_element_list.accept(self)
        else:
            bb_cases = []

        bb_else = self.ctx.function.append_basic_block('switch.case.else')
        bb_exit = self.ctx.function.append_basic_block('switch.exit')

        self.ctx.builder.position_at_end(bb_else)
        if node.otherwise:
            node.otherwise.accept(self)
        self.ctx.builder.branch(bb_exit)

        self.ctx.builder.position_at_end(bb_switch)
        switch = self.ctx.builder.switch(value.handle, bb_else, len(bb_cases))

        for case_val, case_enter, case_exit in bb_cases:
            self.ctx.builder.position_at_end(case_exit)
            self.ctx.builder.branch(bb_exit)
            switch.add_case(case_val.handle, case_enter)

        self.ctx.builder.position_at_end(bb_exit)

    def visit_CaseListElementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseListElementNode)

        values = node.case_constant_list.accept(self)

        l = []
        for val in values:
            bb_enter = self.ctx.function.append_basic_block(
                                        'switch.case.enter')
            bb_exit = self.ctx.function.append_basic_block('switch.case.exit')
            self.ctx.builder.position_at_end(bb_enter)

            if node.statement:
                node.statement.accept(self)

            self.ctx.builder.branch(bb_exit)

            l.append((val, bb_enter, bb_exit))

        return l

    def visit_CaseConstNode(self, node, arg=None):
        assert isinstance(node, ast.CaseConstNode)

        return node.constant.accept(self, arg)

    def visit_CaseRangeNode(self, node, arg=None):
        assert isinstance(node, ast.CaseRangeNode)

        lo = node.type.lo
        hi = node.type.hi

        l = []

        for val in range(lo, hi + 1):
            type_ = self.ctx.typegen(node.type)
            handle = lc.Constant.int(type_, val)
            l.append(symtab.ConstantValue(handle, node.type))

        return l

    def visit_GotoNode(self, node, arg=None):
        assert isinstance(node, ast.GotoNode)

        lbl = node.label.accept(self, arg)
        block = self.ctx.find_goto(lbl)

        jmp_bb = self.ctx.function.append_basic_block('jump.%s' % lbl)
        cont_bb = self.ctx.function.append_basic_block('unreachable.%s' % lbl)

        self.ctx.builder.branch(jmp_bb)
        block.entries.append(jmp_bb)

        if block.handle:
            self.ctx.builder.position_at_end(jmp_bb)
            self.ctx.builder.branch(block.handle)

        # might be unreachable
        self.ctx.builder.position_at_end(cont_bb)

    def visit_LabeledStatementNode(self, node, arg=None):
        assert isinstance(node, ast.LabeledStatementNode)

        lbl = node.label.accept(self)
        block = self.ctx.find_goto(lbl)

        block.handle = self.ctx.function.append_basic_block('stmt.%s' % lbl)
        self.ctx.builder.branch(block.handle)

        for jmp_bb in block.entries:
            self.ctx.builder.position_at_end(jmp_bb)
            self.ctx.builder.branch(block.handle)

        self.ctx.builder.position_at_end(block.handle)
        node.stmt.accept(self)

######################
#    Expressions     #
######################

    def visit_UnaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.UnaryOpNode)

        expr = node.expr.accept(self)

        if node.name == '-':
            return self.ctx.neg(expr)
        if node.name == '+':
            return expr
        elif node.name == 'not':
            return self.ctx.not_(expr)
        else:
            raise CodegenNodeException(node, "unknown unary operator '%s'" %
                                             node.name)

    def visit_BinaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.BinaryOpNode)

        sign = node.op.name
        left = node.left.accept(self)
        right = node.right.accept(self)

        ops = {'+': self.ctx.add,
               '-': self.ctx.sub,
               '*': self.ctx.mul,
               '/': self.ctx.div,
               'div': self.ctx.div,
               'mod': self.ctx.mod,
               'and': self.ctx.and_,
               'or': self.ctx.or_,
               '=': self.ctx.cmp_eq,
               '<>': self.ctx.cmp_neq,
               '>': self.ctx.cmp_gt,
               '>=': self.ctx.cmp_ge,
               '<': self.ctx.cmp_lt,
               '<=': self.ctx.cmp_le,
               'in': self.ctx.in_}

        if sign in ops.keys():
            op = ops[sign]
            return op(left, right)

        raise CodegenNodeException(node, "unknown binary operator '%s'" % sign)

######################
#    Statements      #
######################

    def visit_TypeConvertNode(self, node, arg=None):
        assert isinstance(node, ast.TypeConvertNode)

        value = node.child.accept(self)
        converted = self.ctx.coerce(value, node.type)

        if not converted:
            converted = self.ctx.cast(value, node.type)

        return converted

    def visit_AssignmentNode(self, node, arg=None):
        assert isinstance(node, ast.AssignmentNode)

        var = node.var_access.accept(self)
        expr = node.expr.accept(self)

        if isinstance(expr.type, symtab.StringType):
            types = []
            types.append(lc.Type.pointer(self.ctx.typegen(var.type.element)))
            types.append(lc.Type.pointer(self.ctx.typegen(expr.type.element)))
            types.append(lc.Type.int(32))

            func = lc.Function.intrinsic(self.ctx.module, lc.INTR_MEMCPY, types)
            args = []
            args.append(self.ctx.builder.bitcast(var.handle, types[0]))
            args.append(self.ctx.builder.bitcast(expr.handle, types[1]))
            args.append(c_int(expr.type.range.hi - expr.type.range.lo + 1))
            args.append(c_int(0))
            args.append(c_bool(False))
            self.ctx.builder.call(func, args)
        else:
            self.ctx.builder.store(expr.handle, var.handle)

    def visit_ArgumentNode(self, node, params=None):
        assert isinstance(node, ast.ArgumentNode)

        return node.expr.accept(self)

    def visit_FunctionCallNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionCallNode)

        name = node.identifier.accept(self)
        if node.arg_list:
            args = node.arg_list.accept(self)
        else:
            args = []

        # User-defined functions
        try:
            func = self.ctx.find_function(name)
            return self.ctx.call(func, args)
        except symtab.SymtabException:
            pass

        # Built-in functions
        try:
            func, args = self.ctx.translate_call(name, args)
            return self.ctx.call(func, args)
        except CodegenException:
            pass

        # Transfer function for enums
        try:
            ty = self.ctx.find_typedef(name)
        except symtab.SymtabException:
            raise CodegenNodeException(node, "call to unknown function '%s'" %
                                              name)
        if len(args) != 1:
            raise CodegenNodeException(node,
                                       "the transfer function '%s' require "
                                       "exactly one argument" % name)

        value = self.ctx.cast(args[0], ty)
        if not value:
            raise CodegenNodeException(node, "casting from '%s' to '%s'" %
                                             (args[0].type, ty))

        return value

######################
#  Variable access   #
######################

    def visit_VarAccessNode(self, node, arg=None):
        assert isinstance(node, ast.VarAccessNode)

        name = node.identifier.accept(self)

        try:
            sym = self.ctx.find_symbol(name)
            if isinstance(sym.type, symtab.ReferenceType):
                handle = self.ctx.builder.load(sym.handle)
                return symtab.VariableValue(handle, sym.type.referee)
            else:
                return sym
        except symtab.SymtabException:
            pass

        # User-defined functions
        try:
            func = self.ctx.find_function(name)
            return self.ctx.call(func)
        except symtab.SymtabException:
            pass

        # Built-in functions
        try:
            func, _ = self.ctx.translate_call(name, [])
            return self.ctx.call(func)
        except CodegenException:
            pass

        raise CodegenNodeException(node, "call to unknown function '%s'" %
                                         name)

    def visit_PointerAccessNode(self, node, arg=None):
        assert isinstance(node, ast.PointerAccessNode)

        var = node.var_access.accept(self);
        load = self.ctx.builder.load(var.handle)

        return symtab.ConstantValue(load, node.type)


    def visit_IndexedVarNode(self, node, field=None):
        assert isinstance(node, ast.IndexedVarNode)

        arr = node.var_access.accept(self)
        arr_ty = arr.type

        indices = [c_int(0)]

        for i in node.index_expr_list.accept(self):
            width = i.type.width

            value = c_int(arr_ty.range.lo, width)
            value = self.ctx.builder.sub(i.handle, value)

            indices.append(value)

            arr_ty = arr_ty.element

        handle = self.ctx.builder.gep(arr.handle, indices)

        return symtab.VariableValue(handle, node.type)

    def visit_FieldAccessNode(self, node, arg=None):
        assert isinstance(node, ast.FieldAccessNode)

        name = node.identifier.accept(self)
        var = node.var_access.accept(self)

        offset = 0
        for field in node.var_access.type.fields:
            if field.name == name:
                indices = [c_int(0), c_int(offset)]
                handle = self.ctx.builder.gep(var.handle, indices)
                return symtab.VariableValue(handle, node.type)
            else:
                offset += 1

        variant = node.var_access.type.variant
        if not variant:
            raise CodegenNodeException(node, "unknown field '%s'" % name)

        elif variant.selector.name == name:
            indices = [c_int(0), c_int(offset)]
            handle = self.ctx.builder.gep(var.handle, indices)
            return symtab.VariableValue(handle, node.type)

        offset += 1

        for case in variant.cases:
            case_offset = 0
            for field in case.fields:
                if field.name == name:
                    indices = [c_int(0), c_int(offset)]
                    handle = self.ctx.builder.gep(var.handle, indices)

                    type_ = self.ctx.typegen(case)
                    handle = self.ctx.builder.bitcast(handle,
                                                      lc.Type.pointer(type_))

                    indices = [c_int(0), c_int(case_offset)]
                    handle = self.ctx.builder.gep(handle, indices)

                    return symtab.VariableValue(handle, field.type)
                else:
                    case_offset += 1

        raise CodegenNodeException(node, "unknown field '%s'" % name)

    def visit_VarReferenceNode(self, node, arg=None):
        assert isinstance(node, ast.VarReferenceNode)

        sym = node.var_access.accept(self)
        ty = symtab.ReferenceType(sym.type)

        return symtab.VariableValue(sym.handle, ty)

    def visit_VarLoadNode(self, node, arg=None):
        assert isinstance(node, ast.VarLoadNode)

        var = node.var_access.accept(self)
        if isinstance(var, symtab.ConstantValue):
            return var

        load = self.ctx.builder.load(var.handle)

        if (isinstance(node.type, symtab.IntRangeType) or
            isinstance(node.type, symtab.CharRangeType)):
            type_ = self.ctx.typegen(node.type)
            lo = lc.Constant.int(type_, node.type.lo)
            hi = lc.Constant.int(type_, node.type.hi)

            #md = lc.MetaData.get(self.ctx.module, [lo, hi])
            #load.set_metadata('range', md)

        return symtab.ConstantValue(load, node.type)

######################
#     Terminals      #
######################

    def visit_LabelNode(self, node, arg=None):
        assert isinstance(node, ast.LabelNode)

        return node.name

    def visit_IdentifierNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierNode)

        return node.name

    def visit_CharNode(self, node, arg=None):
        assert isinstance(node, ast.CharNode)

        type_ = self.ctx.typegen(node.type)
        value = lc.Constant.int(type_, ord(node.value))

        return symtab.ConstantValue(value, node.type)

    def visit_IntegerNode(self, node, arg=None):
        assert isinstance(node, ast.IntegerNode)

        type_ = self.ctx.typegen(node.type)
        value = lc.Constant.int(type_, node.value)

        return symtab.ConstantValue(value, node.type)

    def visit_RealNode(self, node, arg=None):
        assert isinstance(node, ast.RealNode)

        type_ = self.ctx.typegen(node.type)
        value = lc.Constant.real(type_, node.value)

        return symtab.ConstantValue(value, node.type)

    def visit_SetNode(self, node, arg=None):
        assert isinstance(node, ast.SetNode)

        members = node.member_list.accept(self)

        ty = symtab.UIntType(node.type.width)
        handle = c_int(0, node.type.width)

        for m in members:
            m = self.ctx.cast(m, ty)
            one = c_int(1, node.type.width)

            if not self.ctx.builder:
                one = one.shl(m.handle)
                handle = handle.or_(one)
            else:
                one = self.ctx.builder.shl(one, m.handle)
                handle = self.ctx.builder.or_(handle, one)

        return symtab.ConstantValue(handle, ty)

    def visit_SetMemberRangeNode(self, node, arg=None):
        assert isinstance(node, ast.SetMemberRangeNode)

        start = node.member.accept(self)
        stop = node.expr.accept(self)

        if not hasattr(start.handle, 'z_ext_value'):
            raise CodegenNodeException(node.member,
                                       "todo: variables in set ranges")

        if not hasattr(stop.handle, 'z_ext_value'):
            raise CodegenNodeException(node.expr,
                                       "todo: variables in set ranges")

        # TODO: allow set range members to be variables
        lo = start.handle.z_ext_value
        hi = stop.handle.z_ext_value

        l = []

        for val in range(lo, hi + 1):
            type_ = self.ctx.typegen(node.type)
            handle = lc.Constant.int(type_, val)
            l.append(symtab.ConstantValue(handle, start.type))

        return l

    def visit_SetEmptyNode(self, node, arg=None):
        assert isinstance(node, ast.SetEmptyNode)

        type_ = self.ctx.typegen(node.type)
        value = lc.Constant.int(type_, 0)

        return symtab.ConstantValue(value, node.type)

    def visit_NullNode(self, node, arg=None):
        assert isinstance(node, ast.NullNode)

        type_ = self.ctx.typegen(node.type)
        value = lc.Constant.null(type_)

        return symtab.ConstantValue(value, node.type)

    def visit_StringNode(self, node, arg=None):
        assert isinstance(node, ast.StringNode)

        return self.ctx.c_string(node.value)
