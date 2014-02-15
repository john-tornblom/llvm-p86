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
Implementations of built-in functions in Pascal-86.
'''

from . import symtab as s
from . import log

from llvm import core
from llvm.core import Type
from llvm.core import Constant
from llvm_cbuilder import CDefinition
from llvm_cbuilder import CTemp
from llvm_cbuilder import CVar


mutant_t = Type.opaque('P86.mutant_t')
mutant_t.set_body([Type.int(32), Type.pointer(Type.int(8)),
                  Type.pointer(mutant_t)])


class New(CDefinition):
    '''
    Allocate heap memory
    '''
    _name_ = 'P86.new'
    _retty_ = Type.void()
    _argtys_ = [('ptr', Type.pointer(Type.pointer(Type.int(8)))),
                ('length', Type.int(32))]

    def body(self, ptr, length):
        mem = self.builder.malloc_array(Type.int(8), length.value)
        self.builder.store(mem, ptr.value)
        self.ret()


class Dispose(CDefinition):
    '''
    Free heap memory
    '''
    _name_ = 'P86.dispose'
    _retty_ = Type.void()
    _argtys_ = [('ptr', Type.pointer(Type.pointer(Type.int(8))))]

    def body(self, ptr):
        handle = self.builder.load(ptr.value)
        self.builder.free(handle)

        null = Constant.null(Type.pointer(Type.int(8)))
        self.builder.store(null, ptr.value)
        self.ret()


class Ord(CDefinition):
    '''
    Casts the input into a 16bit integer
    '''
    _name_ = 'P86.ord'
    _retty_ = Type.int(16)
    _argtys_ = [('x', Type.int(32))]

    def body(self, x):
        self.ret(x.cast(Type.int(16)))


class Size(CDefinition):
    '''
    Casts the input into a 32bit integer.
    the sizeof function is resolved at compile time
    '''
    _name_ = 'P86.size'
    _retty_ = Type.int(32)
    _argtys_ = [('x', Type.int(64))]

    def body(self, x):
        self.ret(x.cast(Type.int(32)))


class Chr(CDefinition):
    '''
    Casts the input into a 8bit integer
    '''
    _name_ = 'P86.chr'
    _retty_ = Type.int(8)
    _argtys_ = [('x', Type.int(32))]

    def body(self, x):
        self.ret(x.cast(Type.int(8)))


class Succ(CDefinition):
    '''
    Adds one to the input
    '''
    _name_ = 'P86.succ'
    _retty_ = Type.int(32)
    _argtys_ = [('x', Type.int(32))]

    def body(self, x):
        one = self.constant(x.type, 1)
        succ = x + one
        self.ret(succ)


class Pred(CDefinition):
    '''
    Subtracts one from the input
    '''
    _name_ = 'P86.pred'
    _retty_ = Type.int(32)
    _argtys_ = [('x', Type.int(32))]

    def body(self, x):
        one = self.constant(x.type, 1)
        pred = x - one
        self.ret(pred)


class Odd(CDefinition):
    '''
    Casts the input to a 1bit boolean
    '''
    _name_ = 'P86.odd'
    _retty_ = Type.int(1)
    _argtys_ = [('x', Type.int(32))]

    def body(self, x):
        one = Constant.int(Type.int(1), 1)
        one = CTemp(self, one)
        b = x.cast(Type.int(1))

        self.ret(b and one)


class Trunc(CDefinition):
    '''
    Convenient method that will cast a function call to libc trunc()
    to a 16bit integer.
    '''
    _name_ = 'P86.trunc'
    _retty_ = Type.int(16)
    _argtys_ = [('x', Type.double())]

    def body(self, x):
        mod = self.function.module

        ret = Type.double()
        args = [Type.double()]
        type_ = Type.function(ret, args)
        func = mod.get_or_insert_function(type_, "trunc")

        value = self.builder.call(func, [x.value])
        value = CTemp(self, value)

        self.ret(value.cast(Type.int(16)))


class Ltrunc(CDefinition):
    '''
    Convenient method that will cast a function call to libc trunc()
    to a 32bit integer.
    '''
    _name_ = 'P86.ltrunc'
    _retty_ = Type.int(32)
    _argtys_ = [('x', Type.double())]

    def body(self, x):
        mod = self.function.module

        ret = Type.double()
        args = [Type.double()]
        type_ = Type.function(ret, args)
        func = mod.get_or_insert_function(type_, "trunc")

        value = self.builder.call(func, [x.value])
        value = CTemp(self, value)

        self.ret(value.cast(Type.int(32)))


class Round(CDefinition):
    '''
    Convenient method that will cast a function call to libc round()
    to a 16bit integer.
    '''
    _name_ = 'P86.round'
    _retty_ = Type.int(16)
    _argtys_ = [('x', Type.double())]

    def body(self, x):
        mod = self.function.module

        ret = Type.double()
        args = [Type.double()]
        type_ = Type.function(ret, args)
        func = mod.get_or_insert_function(type_, "round")

        value = self.builder.call(func, [x.value])
        value = CTemp(self, value)

        self.ret(value.cast(Type.int(16)))


class Lround(CDefinition):
    '''
    Convenient method that will cast a function call to libc round()
    to a 32bit integer.
    '''
    _name_ = 'P86.lround'
    _retty_ = Type.int(32)
    _argtys_ = [('x', Type.double())]

    def body(self, x):
        mod = self.function.module

        ret = Type.double()
        args = [Type.double()]
        type_ = Type.function(ret, args)
        func = mod.get_or_insert_function(type_, "round")

        value = self.builder.call(func, [x.value])
        value = CTemp(self, value)

        self.ret(value.cast(Type.int(32)))


class OutByt(CDefinition):
    '''
    Not implemented
    '''
    _name_ = 'P86.outbyt'
    _argtys_ = [('addr', Type.int(16)), ('b', Type.int(8))]

    def body(self, addr, b):
        self.ret()


class OutWrd(CDefinition):
    '''
    Not implemented
    '''
    _name_ = 'P86.outwrd'
    _argtys_ = [('addr', Type.int(16)), ('w', Type.int(16))]

    def body(self, addr, w):
        self.ret()


class SetInterrupt(CDefinition):
    '''
    Not implemented, innterupts are not supported.
    '''
    _name_ = 'P86.setinterrupt'
    _argtys_ = [('num', Type.int(16))]

    def body(self, num):
        self.ret()


class EnableInterrupts(CDefinition):
    '''
    Not implemented, innterupts are not supported.
    '''
    _name_ = 'P86.enableinterrupts'

    def body(self):
        self.ret()


class DisableInterrupts(CDefinition):
    '''
    Not implemented, innterupts are not supported.
    '''
    _name_ = 'P86.disableinterrupts'

    def body(self):
        self.ret()


class ParamCount(CDefinition):
    '''
    ParamCount is a Borland Pascal extension and corresponds
    to argc in the C world.
    '''

    _name_ = 'P86.paramcount'
    _retty_ = Type.int(32)

    def body(self):
        mod = self.function.module

        argc_type = core.Type.int(32)
        argc_handle = core.GlobalVariable.new(mod, argc_type, 'P86.argc')
        argc_handle.initializer = core.Constant.undef(argc_type)
        argc_handle.linkage = core.LINKAGE_INTERNAL

        one = self.constant(argc_type, 1)

        value = self.builder.load(argc_handle)
        self.ret(CTemp(self, value) - one)


class ParamStr(CDefinition):
    '''
    ParamStr is a Borland Pascal extension and corresponds
    to argv in the C world.
    '''
    _name_ = 'P86.paramstr'
    _argtys_ = [('x', Type.int(16))]
    _retty_ = Type.pointer(Type.int(8))

    def body(self, x):
        mod = self.function.module

        argv_type = core.Type.pointer(Type.pointer(Type.int(8)))
        argv_handle = core.GlobalVariable.new(mod, argv_type, 'P86.argv')
        argv_handle.initializer = Constant.undef(argv_type)
        argv_handle.linkage = core.LINKAGE_INTERNAL

        var = CVar(self, argv_handle)

        val = var[x]

        self.ret(CTemp(self, val.value))


class SetMutation(CDefinition):
    '''
    Sets the active mutant by iterating the list of mutants until
    the Nth (index) mutant is selected
    '''
    _name_ = 'P86.setmutation'
    _argtys_ = [('index', Type.int(32))]

    def body(self, index):
        mod = self.function.module
        c_int32 = lambda val: Constant.int(Type.int(32), val)

        # global place holder for current mutant id
        id_var = mod.add_global_variable(Type.int(32), "P86.mutant_id")
        id_var.initializer = Constant.int(Type.int(32), 0)
        id_var.linkage = core.LINKAGE_EXTERNAL

        # global place holder module name containing the currently
        # selected mutant
        str_var = mod.add_global_variable(Type.pointer(Type.int(8)),
                                          "P86.mutant_mod")
        str_var.initializer = Constant.null(Type.pointer(Type.int(8)))
        str_var.linkage = core.LINKAGE_EXTERNAL

        # pointer to the tail of the mutant list (reverse order)
        lst_var = mod.add_global_variable(Type.pointer(mutant_t),
                                          "P86.mutant_list")
        lst_var.initializer = Constant.null(Type.pointer(mutant_t))
        lst_var.linkage = core.LINKAGE_EXTERNAL

        ptr = self.var(Type.pointer(mutant_t), self.builder.load(lst_var))
        zero = self.constant(Type.int(32), 0)
        one = self.constant(Type.int(32), 1)

        # index zero disables all mutants
        with self.ifelse(index == zero) as ifelse:
            with ifelse.then():
                self.builder.store(id_var.initializer, id_var)
                self.builder.store(str_var.initializer, str_var)
                self.ret()

        # iterate the list until we get to the Nth element
        with self.loop() as loop:
            with loop.condition() as setcond:
                setcond(index > one)

            with loop.body():
                nxt = self.builder.gep(ptr.value, [c_int32(0), c_int32(2)])
                ptr.assign(CVar(self, nxt))
                index -= one

        # assign mutant id
        handle = self.builder.gep(ptr.value, [c_int32(0), c_int32(0)])
        handle = self.builder.load(handle)
        self.builder.store(handle, id_var)

        # assign module name containing the mutant
        handle = self.builder.gep(ptr.value, [c_int32(0), c_int32(1)])
        handle = self.builder.load(handle)
        self.builder.store(handle, str_var)

        self.ret()


class GetMutationId(CDefinition):
    '''
    Convenient function to expose the currently selected mutant
    '''
    _name_ = 'P86.getmutationid'
    _retty_ = Type.int(32)

    def body(self):
        mod = self.function.module

        var = mod.get_global_variable_named("P86.mutant_id")

        value = self.builder.load(var)
        self.ret(CTemp(self, value))


class GetMutationMod(CDefinition):
    '''
    Convenient function to expose the module the current mutant
    is located in.
    '''
    _name_ = 'P86.getmutationmod'
    _retty_ = Type.pointer(Type.int(8))

    def body(self):
        mod = self.function.module

        var = mod.get_global_variable_named("P86.mutant_mod")

        value = self.builder.load(var)
        self.ret(CTemp(self, value))


class GetMutationCount(CDefinition):
    '''
    Convenient function to expose the number of mutants
    '''
    _name_ = 'P86.getmutationcount'
    _retty_ = Type.int(32)

    def body(self):
        mod = self.function.module

        cnt_var = mod.add_global_variable(Type.int(32), "P86.mutant_count")
        cnt_var.initializer = Constant.int(Type.int(32), 0)
        cnt_var.linkage = core.LINKAGE_EXTERNAL

        self.ret(CTemp(self, self.builder.load(cnt_var)))


class SetMutationId(CDefinition):
    '''
    Sets the active mutant by iterating the list of mutants until
    it finds the requested id. If the id is not in the list, the
    mutant will be set to zero (no mutant active).
    '''
    _name_ = 'P86.setmutationid'
    _argtys_ = [('idx', Type.int(32))]

    def body(self, idx):

        get_id = self.get_function_named('P86.getmutationid')
        get_cnt = self.get_function_named('P86.getmutationcount')
        set_mut = self.get_function_named('P86.setmutation')

        index = self.var(Type.int(32), 0)
        one = self.constant(Type.int(32), 1)
        zero = self.constant(Type.int(32), 0)
        cnt = get_cnt()

        with self.loop() as loop:
            with loop.condition() as setcond:
                setcond(index <= cnt)

            with loop.body():
                set_mut(index)
                with self.ifelse(get_id() == idx) as ifelse:
                    with ifelse.then():
                        set_mut(index)
                        self.ret()
                index += one

        set_mut(zero)
        self.ret()


class CTor(CDefinition):
    '''
    Creates a module constructor used for initializing mutants generated
    in different modules.

    The compiler might generate mutants in different modules. To gain access
    to all mutants between modules, each list needs to be merged after linking.
    This is done using magic provided by llvm.global_ctors (appending linkage).
    Each module provides its own implementation of a CTor, that are executed
    before the main function is called.
    '''
    def __init__(self, name, mutants):
        CTor._name_ = 'P86.ctor.%s' % name
        self.mutants = mutants

    def body(self):
        mod = self.function.module

        c_int32 = lambda val: Constant.int(Type.int(32), val)

        for id_val in self.mutants:
            # allocate memory for mutant info
            handle = self.builder.malloc(mutant_t)

            # set mutant id
            id_val = Constant.int(mutant_t.elements[0], id_val)
            id_var = self.builder.gep(handle, [c_int32(0), c_int32(0)])
            self.builder.store(id_val, id_var)

            # set the module id
            str_val = self.constant_string(mod.id).value
            str_var = self.builder.gep(handle, [c_int32(0), c_int32(1)])
            self.builder.store(str_val, str_var)

            # set the pointer to the next mutant info
            ptr_var = self.builder.gep(handle, [c_int32(0), c_int32(2)])

            try:
                lst_var = mod.get_global_variable_named("P86.mutant_list")
            except:
                lst_var = mod.add_global_variable(Type.pointer(mutant_t),
                                                  "P86.mutant_list")
                lst_var.linkage = core.LINKAGE_EXTERNAL

            lst_val = self.builder.load(lst_var)
            self.builder.store(lst_val, ptr_var)
            self.builder.store(handle, lst_var)

            # increment the total number of mutants
            try:
                cnt_var = mod.get_global_variable_named("P86.mutant_count")
            except:
                cnt_var = mod.add_global_variable(Type.int(32),
                                                  "P86.mutant_count")
                cnt_var.linkage = core.LINKAGE_EXTERNAL

            one = Constant.int(Type.int(32), 1)
            cnt_val = self.builder.load(cnt_var)
            handle = self.builder.add(cnt_val, one)

            self.builder.store(handle, cnt_var)

        self.ret()


def _declare_builtin(mod, cls):
    assert isinstance(cls, type)
    assert CDefinition in cls.__bases__

    ret = cls._retty_
    args = [x[1] for x in cls._argtys_]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, cls._name_)


def f_new(mod):
    return _declare_builtin(mod, New)


def f_dispose(mod):
    return _declare_builtin(mod, Dispose)


def f_ord(mod):
    return _declare_builtin(mod, Ord)


def f_size(mod):
    return _declare_builtin(mod, Size)


def f_chr(mod):
    return _declare_builtin(mod, Chr)


def f_succ(mod):
    return _declare_builtin(mod, Succ)


def f_pred(mod):
    return _declare_builtin(mod, Pred)


def f_odd(mod):
    return _declare_builtin(mod, Odd)


def f_trunc(mod):
    return _declare_builtin(mod, Trunc)


def f_ltrunc(mod):
    return _declare_builtin(mod, Ltrunc)


def f_round(mod):
    return _declare_builtin(mod, Round)


def f_lround(mod):
    return _declare_builtin(mod, Lround)


def f_paramcount(mod):
    return _declare_builtin(mod, ParamCount)


def f_paramstr(mod):
    return _declare_builtin(mod, ParamStr)


def f_outbyt(mod):
    return _declare_builtin(mod, OutByt)


def f_outwrd(mod):
    return _declare_builtin(mod, OutWrd)


def f_setinterrupt(mod):
    return _declare_builtin(mod, SetInterrupt)


def f_enableinterrupts(mod):
    return _declare_builtin(mod, EnableInterrupts)


def f_disableinterrupts(mod):
    return _declare_builtin(mod, DisableInterrupts)


def f_set_mutation(mod):
    '''
    built-in: selects the current mutant.
    '''
    return _declare_builtin(mod, SetMutation)


def f_get_mutation_id(mod):
    '''
    built-in: returns the id of the currently selected mutant
    '''
    return _declare_builtin(mod, GetMutationId)


def f_set_mutation_id(mod):
    '''
    built-in: tries to set the the selected mutant to a new id
    '''
    return _declare_builtin(mod, SetMutationId)


def f_get_mutation_mod(mod):
    '''
    built-in: returns a pointer to the module name
    corresponding to the currently selected mutant.
    '''
    return _declare_builtin(mod, GetMutationMod)


def f_get_mutation_count(mod):
    '''
    built-in: calculates the number of mutations AFTER linking
    '''
    return _declare_builtin(mod, GetMutationCount)


def f_module_constructor(mod):
    '''
    built-in: initializes the mutation functions
    '''
    return _declare_builtin(mod, CTor)


def _llvm_to_symtab(type_):
    if type_.kind == core.TYPE_VOID:
        return s.VoidType()
    elif type_.kind == core.TYPE_INTEGER:
        return s.SIntType(type_.width)
    elif type_.kind == core.TYPE_FLOAT:
        return s.FloatType()
    elif type_.kind == core.TYPE_DOUBLE:
        return s.DoubleType()
    elif type_.kind == core.TYPE_POINTER:
        # Assume all char pointers are strings
        if (type_.pointee.kind == core.TYPE_INTEGER and
            type_.pointee.width == 8):
            return s.StringType(0)
        else:
            referee_ty = _llvm_to_symtab(type_.pointee)
            return s.ReferenceType(referee_ty)
    else:
        log.e('fn', 'unknown llvm type %s' % type_)


def translate_function(func):
    '''
    Converts a function from the internal symtab format
    into llvmpy format.
    '''
    type_ = func.type.pointee
    ret_ty = _llvm_to_symtab(type_.return_type)

    module = 'P86'
    name = func.name
    if '.' in name:
        module, name = name.split('.', 1)

    ty = s.FunctionType(module, name, ret_ty)

    for i, arg in enumerate(type_.args):
        arg_ty = _llvm_to_symtab(arg)
        arg_name = "arg%d" % i
        param = s.ParameterType(arg_name, arg_ty)
        ty.params.append(param)

    return ty


def _install_function(ctx, func):
    ty = translate_function(func)
    ctx.install_function(func.name, ty, func)


def f_printf(mod):
    '''libc: formatted output conversion'''
    ret = Type.int(32)
    arg = Type.pointer(Type.int(8))

    type_ = Type.function(ret, [arg], True)
    return mod.get_or_insert_function(type_, "printf")


def f_scanf(mod):
    '''libc: input format conversion'''
    ret = Type.int(32)
    arg = Type.pointer(Type.int(8))

    type_ = Type.function(ret, [arg], True)
    return mod.get_or_insert_function(type_, "scanf")


def f_pow(mod):
    '''libc: power function'''
    ret = Type.double()
    args = [Type.double(), Type.double()]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "pow")


def f_powf(mod):
    '''libc: power function'''
    ret = Type.float()
    args = [Type.float(), Type.float()]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "powf")


def f_sqrt(mod):
    '''libc: square root function'''
    ret = Type.double()
    args = [Type.double()]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "sqrt")


def f_sqrtf(mod):
    '''libc: square root function'''
    ret = Type.float()
    args = [Type.float()]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "sqrtf")


def f_roundf(mod):
    '''libc: round to nearest integer, away from zero'''
    ret = Type.float()
    args = [Type.float()]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "roundf")


def f_abs(mod):
    '''libc: compute the absolute value of an integer'''
    ret = Type.int()
    args = [Type.int()]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "abs")


def f_fabs(mod):
    '''libc: absolute value of floating-point number'''
    ret = Type.double()
    args = [Type.double()]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "fabs")


def f_random(mod):
    '''libc: random number generator'''
    ret = Type.int(32)
    type_ = Type.function(ret, [])
    return mod.get_or_insert_function(type_, "random")


def f_srandom(mod):
    '''libc: random number generator'''
    ret = Type.void()
    arg = Type.int(32)
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "srandom")


def f_time(mod):
    '''libc: get time in seconds'''
    ret = Type.int(32)
    type_ = Type.function(ret, [])
    return mod.get_or_insert_function(type_, "time")


def f_arccos(mod):
    '''libc: arc cosine function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "acos")


def f_arcsin(mod):
    '''libc: arc sine function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "asin")


def f_arctan(mod):
    '''libc: arc tangent function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "atan")


def f_cos(mod):
    '''libc: cosine function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "cos")


def f_sin(mod):
    '''libc: sine function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "sin")


def f_tan(mod):
    '''libc: tangent function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "tan")


def f_exp(mod):
    '''libc: base-e exponential function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "exp")


def f_ln(mod):
    '''libc: natural logarithmic function'''
    ret = Type.double()
    arg = Type.double()
    type_ = Type.function(ret, [arg])
    return mod.get_or_insert_function(type_, "log")


def f_exit(mod):
    '''libc: cause normal process termination'''
    ret = Type.void()
    args = [Type.int(32)]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "exit")


def f_atoi(mod):
    '''libc: convert a string to an integer'''
    ret = Type.int(32)
    args = [Type.pointer(Type.int(8))]

    type_ = Type.function(ret, args)
    return mod.get_or_insert_function(type_, "atoi")


def f_main(mod):
    '''main function'''
    argc = Type.int(32)
    argv = Type.pointer(Type.pointer(Type.int(8)))
    type_ = Type.function(Type.void(), [argc, argv])

    return mod.get_or_insert_function(type_, "main")


def define_libp86(ctx):
    '''
    Defines built-in functions defined by Pascal-86
    '''
    _install_function(ctx, New()(ctx.module))
    _install_function(ctx, Dispose()(ctx.module))
    _install_function(ctx, Ord()(ctx.module))
    _install_function(ctx, Size()(ctx.module))
    _install_function(ctx, Chr()(ctx.module))
    _install_function(ctx, Succ()(ctx.module))
    _install_function(ctx, Pred()(ctx.module))
    _install_function(ctx, Odd()(ctx.module))
    _install_function(ctx, Trunc()(ctx.module))
    _install_function(ctx, Ltrunc()(ctx.module))
    _install_function(ctx, Round()(ctx.module))
    _install_function(ctx, Lround()(ctx.module))
    _install_function(ctx, ParamCount()(ctx.module))
    _install_function(ctx, ParamStr()(ctx.module))
    _install_function(ctx, OutByt()(ctx.module))
    _install_function(ctx, OutWrd()(ctx.module))
    _install_function(ctx, SetInterrupt()(ctx.module))
    _install_function(ctx, EnableInterrupts()(ctx.module))
    _install_function(ctx, DisableInterrupts()(ctx.module))


def declare_libp86(ctx):
    '''
    Declares built-in functions defined by Pascal-86
    '''
    _install_function(ctx, f_ord(ctx.module))
    _install_function(ctx, f_size(ctx.module))
    _install_function(ctx, f_chr(ctx.module))
    _install_function(ctx, f_succ(ctx.module))
    _install_function(ctx, f_pred(ctx.module))
    _install_function(ctx, f_odd(ctx.module))
    _install_function(ctx, f_trunc(ctx.module))
    _install_function(ctx, f_ltrunc(ctx.module))
    _install_function(ctx, f_round(ctx.module))
    _install_function(ctx, f_lround(ctx.module))
    _install_function(ctx, f_paramcount(ctx.module))
    _install_function(ctx, f_paramstr(ctx.module))
    _install_function(ctx, f_setinterrupt(ctx.module))
    _install_function(ctx, f_enableinterrupts(ctx.module))
    _install_function(ctx, f_disableinterrupts(ctx.module))
    _install_function(ctx, f_outbyt(ctx.module))
    _install_function(ctx, f_outwrd(ctx.module))


def define_mutation(ctx):
    '''
    Defines built-in mutation functions
    '''
    _install_function(ctx, SetMutation()(ctx.module))
    _install_function(ctx, GetMutationId()(ctx.module))
    _install_function(ctx, GetMutationCount()(ctx.module))
    _install_function(ctx, GetMutationMod()(ctx.module))
    _install_function(ctx, SetMutationId()(ctx.module))


def declare_mutation(ctx):
    '''
    Declares built-in mutation functions
    '''
    _install_function(ctx, f_set_mutation(ctx.module))
    _install_function(ctx, f_get_mutation_id(ctx.module))
    _install_function(ctx, f_get_mutation_mod(ctx.module))
    _install_function(ctx, f_get_mutation_count(ctx.module))


def define_ctor(ctx, mutants):
    '''
    sets up global ctor that will initialize a linked list
    with mutant information
    '''
    fn = CTor(ctx.module.id, mutants)(ctx.module)

    value = Constant.int(Type.int(32), 65535)
    value = Constant.struct([value, fn])
    value = Constant.array(value.type, [value])

    ctors = ctx.module.add_global_variable(value.type, "llvm.global_ctors")
    ctors.linkage = core.LINKAGE_APPENDING
    ctors.initializer = value
