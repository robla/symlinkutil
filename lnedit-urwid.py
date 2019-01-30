#!/usr/bin/python3
"""
A TUI for editing symlinks
"""

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

import argparse
import os
import symlink_ui_urwid
import sys


def get_userroot():
    userroot = os.path.realpath(os.readlink(".userroot"))
    userroot = os.getenv('USERROOT')
    return userroot


def get_values_from_link(linkname):
    """
    Read a symlink at the given linkname, and return a dict for passing
    into the UI.
    """

    retval = {}
    # first add the core data:

    retval['origlink'] = linkname
    symlinkpath = os.readlink(linkname)
    retval['targetref'] = symlinkpath

    # suggestion #1 - absolute path
    oldhome = os.path.realpath(symlinkpath)
    retval['suggestion-abspath'] = oldhome

    # suggestion #2 - relative path to pwd
    realpwd = os.path.realpath(os.getenv('PWD'))
    newhome = os.path.normpath(os.path.join(realpwd, linkname))
    symtarg_relpath = os.path.relpath(newhome, os.path.dirname(oldhome))
    retval['suggestion-relpath'] = symtarg_relpath

    # suggestion #3 - .userroot alternative
    rel_to_userroot = os.path.relpath(oldhome, get_userroot())
    symtarg_userroot = os.path.join('.userroot', rel_to_userroot)
    retval['suggestion-userroot'] = symtarg_userroot

    return retval


def make_the_move(origlink, newtargetref, allowbroken=False):
    # FIXME: put the imports at the top of the file
    from pathlib import Path
    import shutil
    newtarg = Path(newtargetref)

    if newtarg.exists() or allowbroken:
        # TODO: make this atomic by creating and moving the new symlink over
        # the old one, rather than deleting then moving.
        os.remove(origlink)
        os.symlink(newtargetref, origlink)
    else:
        raise FileNotFoundError(newtargetref)
    retval = "{} links to {}".format(origlink, newtargetref)
    if not newtarg.exists():
        retval += "\nNOTE: {} doesn't appear to exist.".format(newtargetref)
    return retval


def main(argv=None):
    # using splitlines to just get the first line
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])

    parser.add_argument('-a', '--allow-broken',
                        help='allow resulting broken link', action="store_true")
    parser.add_argument(
        '-j', '--just-print', help='just print the JSON for debugging', action="store_true")
    parser.add_argument('symlink', help='symlink for editing')
    args = parser.parse_args()

    try:
        oldvals = get_values_from_link(args.symlink)
    except OSError:
        print("File '{}' isn't a symlink.".format(args.symlink))
        parser.print_usage()
        sys.exit(1)

    oldvals['allowbroken'] = args.allow_broken
    newvals = symlink_ui_urwid.start_main_loop(oldvals)

    if args.just_print:
        import json
        if newvals == 'cancel':
            print(json.dumps(oldvals, indent=4))
        else:
            print(json.dumps(newvals, indent=4))
        sys.exit()

    try:
        origlink = oldvals['origlink']
        newtargetref = newvals['targetref']
    except TypeError:
        sys.exit()
    try:
        status = make_the_move(origlink, newtargetref,
                               allowbroken=newvals['allowbroken'])
        print(status)
    except FileNotFoundError:
        print("File not found: " + newtargetref)
        print("'Allow writing broken symlink' set to '{}'.  Aborting.".format(
            newvals['allowbroken']))


if '__main__' == __name__:
    main()


