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
Tools for generating mutation reports in json format.
'''

import json
import time
import os

from . import log


def c_mul32(a, b):
    '''Simulate a 32bit multiplication in C (overflow)'''
    return eval(hex((long(a) * b) & (2 ** 32 - 1))[:-1])


def hash32(s):
    '''
    Hash a string into a 32bit integer.
    The hash in not secure and may cause collisions
    '''
    if not s:
        return 0  # empty

    value = ord(s[0]) << 7
    for char in s:
        value = c_mul32(1000003, value) ^ ord(char)
        value = value ^ len(s)

    if value == -1:
        value = -2

    if value >= 2 ** 31:
        value -= 2 ** 32

    return value


def default_serializer(o):
    return o.obj()


class MutationReport(object):

    def __init__(self, name, filename, md5_hash):
        self.name = name
        self.filename = filename
        self.md5 = md5_hash
        self.mutations = list()
        self.mutants = list()

    def add_mutant(self, pos, s):
        if pos.path[-1] != os.path.basename(self.filename):
            return None

        id_ = str(self.md5)
        id_ += str(pos.lineno)
        id_ += str(pos.lexpos)
        id_ += str(pos.lexendpos)
        id_ += str(s)
        id_ = hash32(id_)
        id_ = int(id_)

        if id_ not in self.ids():
            mutant = {
                      'id': str(id_),
                      'file': pos.path[-1],
                      'line': pos.lineno,
                      'start': pos.lexpos,
                      'stop': pos.lexendpos,
                      'value': s
                      }

            self.mutants.append(mutant)

        return id_

    @property
    def count(self):
        return len(self.mutants)

    def ids(self):
        l = []

        for m in self.mutants:
            l.append(int(m['id']))

        return l

    def save(self, path):
        log.i("report", "Saving json to %s" % path)
        dir_ = os.path.dirname(path)
        if not os.path.exists(dir_):
            os.makedirs(dir_)

        f = open(path, 'w')
        f.write(str(self))

    def obj(self):
        return {'name': self.name,
                'filename': self.filename,
                'md5': self.md5,
                'timestamp': int(time.time()),
                'mutants': self.mutants}

    def __str__(self):
        return json.dumps(self.obj(), default=default_serializer)
