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
  Logging wrappers.
'''

import logging


def e(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.error(msg, *args, **kwargs)


def w(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.warning(msg, *args, **kwargs)


def i(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.info(msg, *args, **kwargs)


def d(prefix, msg, *args, **kwargs):
    logger = logging.getLogger(prefix)
    logger.debug(msg, *args, **kwargs)


def set_level(name):
    levels = {"error": logging.ERROR,
              "warn": logging.WARNING,
              "info": logging.INFO,
              "debug": logging.DEBUG}

    if name in levels:
        logging.basicConfig(level=levels[name])


def set_verbosity(lvl):
    levels = (logging.ERROR,
              logging.WARNING,
              logging.INFO,
              logging.DEBUG)

    if lvl > len(levels) - 1:
        lvl = len(levels) - 1
    elif lvl < 0:
        lvl = 0

    logging.basicConfig(level=levels[lvl])
