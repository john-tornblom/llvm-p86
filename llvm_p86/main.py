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
Command line interface for an LLVM-based Pascal-86 compiler.
'''

import sys
import os

from . import log
from . import compiler

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

__all__ = []
__version__ = 0.3
__date__ = '2013-01-15'
__updated__ = '2013-10-29'

DEBUG = 0


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def run(argv=None):
    sys.setrecursionlimit(50000)

    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version,
                                                     program_build_date)
    program_shortdesc = 'LLVM-based Pascal compiler'
    program_license = '''%s

  created by John Törnblom on %s.
''' % (program_shortdesc, str(__date__))

    mutation_help = '''Mutate the code using on of the mutation operators.
    sc  - statement coverage
    dcc - decision/condition coverage

    ror - relational operator replacement (<, <=, =, <>, >=, >)
    cor - conditional operator replacement (and, or)
    aor - arithmetic operator replacement (+, -, *, /, div, mod)
    sdl - statement deletion'''

    try:
        # Setup argument parser
        parser = ArgumentParser(prog=program_name, description=program_license, formatter_class=RawTextHelpFormatter)
        parser.add_argument("-t", "--syntax-tree", dest="tree", action="store_true", help="print the syntax tree to stdout")
        parser.add_argument("-S", "--emit-llvm", dest="ir_code", metavar="PATH", action="store", help="save LLVM-IR (plain text) to PATH")
        parser.add_argument("-b", "--bit-code", dest="bit_code", metavar="PATH", action="store", help="save LLVM-IR (bit code) to PATH")
        parser.add_argument("-o", "--object-code", dest="obj_code", metavar="PATH", action="store", help="save object code to PATH")
        parser.add_argument("-c", "--source-code", dest="src_code", metavar="PATH", action="store", help="save source code to PATH")
        parser.add_argument("-O", "--optimize", dest="opt", metavar="LEVEL", action="store", choices=['0', '1', '2', '3'], default='0', help="run various optimizations on the LLVM-IR code")

        parser.add_argument("-T", "--triple", dest="triple", action="store", default='', help="define the target triple, e.g. x86_64-pc-linux or i686-pc-win32")
        parser.add_argument("-mcpu", dest="cpu", default='', help='target specific cpu type')
        parser.add_argument("-mattrs", dest="attrs", default='', help='target specific attributes')

        parser.add_argument("-D", "--define", dest="defs", metavar="DEF", action="append", help="define constants for the preprocessor")
        parser.add_argument("-I", "--include", dest="incs", metavar="PATH", action="append", help="define include directories for the preprocessor")
        parser.add_argument("-e", "--execute", dest="execute", action="store_true", help="execute the main function using the LLVM JIT compiler")
        parser.add_argument("-a", "--arguments", dest="args", metavar="ARGS", action="store", default='', help="optional string with arguments when executing the main function using the JIT compiler")
        parser.add_argument("-r", "--report", dest="report", metavar="PATH", action="store", help="collect information on mutations and store it as json formatted data in the folder PATH")
        parser.add_argument("-m", "--mutation", dest="mutation", action="store", choices=['sc', 'dcc', 'ror', 'cor', 'aor', 'sdl'], help=mutation_help)
        parser.add_argument("-v", "--verbosity", dest="verbosity", action="count", default=0)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="file", metavar="file")

        # Process arguments
        args = parser.parse_args()

        if args.verbosity:
            log.set_verbosity(args.verbosity)
        else:
            log.set_verbosity(0)

        c = compiler.Compiler(args.file)

        if args.defs:
            for d in args.defs:
                c.define(d)

        if args.incs:
            for i in args.incs:
                c.include(i)

        c.analyze()

        if args.tree:
            c.print_tree()

        if args.mutation:
            c.mutate(args.mutation, args.report)

        if args.tree and args.mutation:
            c.print_tree()

        if args.src_code:
            c.save_source_code(args.src_code)

        synthesize = (args.ir_code or args.bit_code or
                      args.obj_code or args.execute)

        if synthesize:
            c.synthesize()

        if args.opt and synthesize:
            c.optimize(int(args.opt))

        if args.ir_code:
            c.save_ir(args.ir_code, args.triple)

        if args.bit_code:
            c.save_bit_code(args.bit_code, args.triple)

        if args.obj_code:
            c.save_obj_code(args.obj_code, args.triple, args.cpu, args.attrs)

        if args.execute:
            c.execute(args.args)

        return 0

    except KeyboardInterrupt:
        return 0
#    except Exception, e:
#        log.e('llvm-p86', str(e))
#        return -1
