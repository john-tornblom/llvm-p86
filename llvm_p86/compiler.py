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
Pascal-86 compiler front end for LLVM with mutation capabilities.
'''

import datetime
import sys
import hashlib
import os
import shutil

from . import pre
from . import tokens
from . import grammar
from . import ast
from . import mutation
from . import typesys
from . import sourcegen
from . import log

try:
    from llvm import ee
    from llvm import passes
    import ctypes
    from . import codegen
    from . import fn
except ImportError:
    print('Cannot find llvmpy, code generation will not function')
    pass


class PrintVisitor(ast.NodeVisitor):

    def __init__(self):
        self.level = 0

    def visit_VarDeclListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_StatementListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_ConstListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_FunctionListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_ParameterListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_ArgumentListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_IdentifierListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_TypeDefListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_RecordSectionListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_CaseListElementListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_CaseConstListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_LabelListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_SetMemberListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def visit_VariantListNode(self, node, arg=None):
        ast.NodeVisitor.default_visit(self, node)

    def default_visit(self, node, arg=None):
        self.print_node(node)

        self.level += 1
        for c in filter(None, node.children):
            if isinstance(c, ast.Node):
                c.accept(self)
            else:
                self.print_string(c)

        self.level -= 1

    def print_string(self, node, arg=None):
        pos = '?'

        prefix = pos + '  \t'
        spacer = ''.join([' ' * (2 * self.level)])
        print((prefix + spacer + str(node)))

    def print_node(self, node, arg=None):
        pos = node.position
        if not pos:
            pos = '?'

        ty = node.type
        if not ty:
            ty = '(?)'

        prefix = str(pos) + '  \t' + str(ty.__class__.__name__[0:-4]) + '  \t'
        # prefix = str(pos) + '  \t' + str(ty) + '  \t'

        spacer = ''.join([' ' * (2 * self.level)])
        print((prefix + spacer + str(node)))


class Compiler(object):

    def __init__(self, filename):
        self.ctx = None
        self.filename = filename
        basename = os.path.basename(filename)
        filename = os.path.splitext(basename)
        self.name = filename[0]

        self.chars = None
        self.hash = None
        self.mutants = []
        self.defines = dict()
        self.includes = ['.']

    def define(self, d):
        d = d.split('=')
        if len(d) == 1:
            key = d[0]
            val = True
        elif len(d) == 2:
            try:
                key = d[0]
                val = eval(d[1])
            except:
                log.w("compiler", "Invalid define syntax '%s=%s'" %
                                  (d[0], d[1]))
                return
        else:
            log.w("compiler", "Invalid define syntax")
            return

        key = key.  lower()
        self.defines[key] = val

    def include(self, path):
        if os.path.isdir(path):
            self.includes.append(path)
        else:
            log.w("compiler", "Invalid include '%s'", path)

    def analyze(self):
        log.d("compiler", "Parsing source code")
        pre.pre_defines = self.defines
        pre.pre_includes = self.includes

        textRoot = pre.process(self.filename)

        hash_code = hashlib.md5()
        hash_code.update(str(textRoot).encode())
        self.hash = hash_code.hexdigest()
        self.mutants = []

        scanner = tokens.scanner()
        parser = grammar.parser()

        # To preserve positional information between files,
        # use a custom token generator
        def token_generator():
            for node in textRoot.nodes:
                #print type(node), node.pos
                if not isinstance(node, pre.TextNode):
                    continue

                scanner.lineno = lineno = 0
                scanner.lexpos = lexpos = 0

                scanner.input(node.value)

                while True:
                    t = scanner.token()
                    if t is None:
                        break

                    lineno = scanner.lineno
                    lexpos = scanner.lexpos

                    scanner.lineno = (node.pos[0],
                                      scanner.lineno + node.pos[1])
                    scanner.lexpos = node.pos[2] + t.lexpos

                    t.lineno = (node.pos[0], t.lineno + node.pos[1])
                    t.lexpos = t.lexpos + node.pos[2]
                    t.endlexpos = t.endlexpos + node.pos[3]

                    yield t

                    scanner.lineno = lineno
                    scanner.lexpos = lexpos

        gen = token_generator()

        def next_token():
            try:
                t = next(gen)
                return t
            except:
                return None

        self.ast = parser.parse(lexer=scanner, tokenfunc=next_token,
                                tracking=True)

        if not self.ast:
            sys.exit(1)

        v = typesys.TypeSetVisitor()
        self.ast.accept(v)

        v = typesys.CallByRefVisitor()
        self.ast.accept(v)

    def mutate(self, mop, rep_path):

        if mop == 'sc':
            mutator = mutation.SCMutationVisitor(self.filename, self.hash)
        elif mop == 'dcc':
            mutator = mutation.DCCMutationVisitor(self.filename, self.hash)
        elif mop == 'ror':
            mutator = mutation.RorMutationVisitor(self.filename, self.hash)
        elif mop == 'cor':
            mutator = mutation.CorMutationVisitor(self.filename, self.hash)
        elif mop == 'aor':
            mutator = mutation.AorMutationVisitor(self.filename, self.hash)
        elif mop == 'sdl':
            mutator = mutation.SdlMutationVisitor(self.filename, self.hash)
        else:
            log.e("compiler", "Unknown mutation operator %s" % mop)
            return

        self.ast.accept(mutator)

        self.mutants = mutator.report.ids()
        log.i("compiler", "Generated %d mutants" % len(self.mutants))

        if rep_path:
            mutator.report.save(rep_path + "/" + self.name + ".json")
            shutil.copy2(self.filename, rep_path + "/" + self.name + ".p")

    def synthesize(self):
        log.d("compiler", "Generating code")
        v = codegen.CodegenVisitor(self.mutants)
        self.ast.accept(v)
        self.ctx = v.ctx

        # verify fails with goto-statements, but compile and run just fine
        # self.ctx.module.verify()

    def optimize(self, level=0):
        log.i("compiler", "Optimizing code at level %d" % level)

        pm = passes.PassManager.new()
        pmb = passes.PassManagerBuilder.new()

        pmb.opt_level = level
        pmb.populate(pm)

        pm.run(self.ctx.module)

    def execute(self, args=''):
        tm = ee.TargetMachine.new(opt=0, cm=ee.CM_JITDEFAULT)
        engine = ee.EngineBuilder.new(self.ctx.module).create(tm)

        func = fn.f_module_constructor(self.ctx.module)
        engine.run_function(func, [])

        func = fn.f_main(self.ctx.module)
        func = engine.get_pointer_to_function(func)

        if len(args):
            args = args.split(' ')
            args.insert(0, self.filename)
        else:
            args = [self.filename]

        args = [x.encode() for x in args]

        ret_ct = ctypes.c_int
        argv_ct = ctypes.ARRAY(ctypes.c_char_p, len(args))
        argc_ct = ctypes.c_int

        FUNC_TYPE = ctypes.CFUNCTYPE(ret_ct, *[argc_ct, argv_ct])
        py_main = FUNC_TYPE(func)

        argc = argc_ct(len(args))
        argv = argv_ct(*args)

        py_main(argc, argv)

    def _open_file(self, path):
        basedir = os.path.dirname(path)
        if not basedir:
            path = os.getcwd() + os.sep + path
            basedir = os.path.dirname(path)

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        return open(path, 'wb')

    def save_source_code(self, out):

        v = sourcegen.SourceVisitor(self.filename)
        src = self.ast.accept(v)
        src = sourcegen.split_long_lines(src, 120)
        src = "(* Generated by llvm-p86 from %s at %s *)\n%s" % (
            self.filename, datetime.datetime.now().strftime("%c"), src)

        if out == '-':
            print(src)
        else:
            f = self._open_file(out)
            f.write(src.encode())
            f.close()

    def save_ir(self, out, triple=''):

        if self.ctx is None or self.ctx.module is None:
            return

        tm = ee.TargetMachine.new(triple)
        self.ctx.module.target = str(tm.triple)
        self.ctx.module.data_layout = str(tm.target_data)

        s = "; Generated by llvm-p86 from %s at %s\n%s" % (
            self.filename, datetime.datetime.now().strftime("%c"),
            self.ctx.module)

        if out == '-':
            print(s)
        else:
            f = self._open_file(out)
            f.write(s.encode())
            f.close()

    def save_bit_code(self, out, triple=''):

        if self.ctx is None or self.ctx.module is None:
            return

        tm = ee.TargetMachine.new(triple)
        self.ctx.module.target = str(tm.triple)
        self.ctx.module.data_layout = str(tm.target_data)

        bc = self.ctx.module.to_bitcode()

        if out == '-':
            os.write(sys.stdout.fileno(), bc)
        else:
            f = self._open_file(out)
            f.write(bc)
            f.close()

    def save_obj_code(self, out, triple='', cpu='', attrs=''):

        if self.ctx is None or self.ctx.module is None:
            return

        tm = ee.TargetMachine.new(triple, cpu, attrs, 0)
        obj = tm.emit_object(self.ctx.module)

        if out == '-':
            os.write(sys.stdout.fileno(), obj)
        else:
            f = self._open_file(out)
            f.write(obj)
            f.close()

    def print_tree(self):
        if self.ast is not None:
            log.d("compiler", "Printing syntax tree for %s" % self.filename)
            self.ast.accept(PrintVisitor())
