#!/usr/bin/python3
# Copyright (c) 2010-2019 Rob Lanphier
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import os
import symlink_ui_urwid


def get_userroot():
    userroot = os.path.realpath(os.readlink(".userroot"))
    userroot = os.getenv('USERROOT')
    return userroot


def get_values_from_link():
    # function copied and adapted from swapln.py

    # our example starts with this pwd:
    # /home/robla/tech/util/timeutil/weekutil/src-timeutil

    retval = {}

    linkname = "18W28tmp"
    retval['origlink'] = linkname

    # should result in ".userroot/tmp/2018/18W28/timeutil"
    symlinkpath = os.readlink("18W28tmp")
    retval['targetref'] = symlinkpath

    # should result in
    # ""/home/robla/poochie14/home/robla/tmp/2018/18W28/timeutil"
    oldhome = os.path.realpath(symlinkpath)

    # realpwd = os.path.realpath(os.getenv('PWD'))
    realpwd = "/home/robla/tech/util/timeutil/weekutil/src-timeutil"

    # should result in
    # "/home/robla/tech/util/timeutil/weekutil/src-timeutil/18W28tmp"
    newhome = os.path.normpath(os.path.join(realpwd, linkname))

    #oldhome = os.getcwd()
    #newhome = os.getenv('PWD')

    # '../../../../../../tech/util/timeutil/weekutil/src-timeutil/18W28tmp'
    symtarg_relpath = os.path.relpath(newhome, os.path.dirname(oldhome))
    retval['targetref-relpath'] = symtarg_relpath

    # '/home/robla/tech/util/timeutil/weekutil/src-timeutil/18W28tmp'
    symtarg_abspath = os.path.abspath(newhome)
    retval['origreadlink'] = symtarg_abspath

    # this should be 'tmp/2018/18W28/timeutil'
    rel_to_userroot = os.path.relpath(oldhome, get_userroot())

    # this should be '.userroot/tmp/2018/18W28/timeutil'
    symtarg_userroot = os.path.join('.userroot', rel_to_userroot)
    retval['targetref-userroot'] = symtarg_userroot

    return retval


def main():    
    defaults = get_values_from_link()
    
    symlink_ui_urwid.start_main_loop(defaults)


if '__main__' == __name__:
    main()
