#!/usr/bin/env python
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

import os
import glob
from distutils.core import setup
from distutils.core import Command

from llvm_p86 import pre
from llvm_p86 import tokens
from llvm_p86 import grammar
from llvm_p86 import main

class PrepareCommand(Command):
    description = "Prepare the source code by generating lexer and parser tables"
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        #build lexer and parser tables
        saved_path = os.getcwd()
        os.chdir(os.path.dirname(pre.__file__))
        os.system('rm _p86*')

        pre.scanner(True)
        pre.parser(True)
        tokens.scanner(True)
        grammar.parser(True)

        os.chdir(saved_path)


# collect data files
js = glob.glob("wwwroot/js/*.js")
css = glob.glob("wwwroot/css/*.css")

long_desc = "llvm-p86 is a compiler and mutation testing framework intended for the "\
"programming language Pascal-86. Compared to a regular compiler, llvm-p86 is "\
"able to create mutated versions of its input and encode several mutants "\
"into a single program"

setup(name='llvm-p86',
      version=str(main.__version__),
      description='Compiler and mutation testing framework for Pascal-86',
      long_description=long_desc,
      author='John Törnblom',
      author_email='john.tornblom@gmail.com',
      url='https://github.com/john-tornblom/llvm-p86',
      license='GPLv3',
      platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      packages=['llvm_p86'],
      requires=['ply', 'llvm'],
      data_files = [('share/llvm-p86/css', css),
                    ('share/llvm-p86/js', js),
                    ('share/llvm-p86/data', ['wwwroot/data/.keep'])],
      scripts=['llvm-p86', 'llvm-p86-webserver'],
      cmdclass={'prepare': PrepareCommand}
      )

