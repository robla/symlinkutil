#!/usr/bin/python3
"""
A TUI for editing symlinks
"""

# Copyright (c) 2019 Rob Lanphier
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

    # FIXME FIXME 2019-01-31
    # What I need to do is to figure out how to calculate the working directory
    # of a symlink.  So, for example, if I have a symlink named "foo" in this
    # directory:
    # /tmp/d1/d2
    # ...and this symlink
    # /tmp/d1/d2/bardir -> /tmp/d1/d3
    # ...and a file named "bar" in this directory
    # /tmp/d1/d3
    # ...and "foo" points to "bar" in d3 via symlink that looks like this:
    # foo -> bardir/bar
    # ...and I call lnedit from d1, like so:
    # lnedit d2/foo
    # ...then I want the suggestion to change the foo link into
    # foo -> ../d3/bar
    # ^^^^ FIXME
    # suggestion #2 - relative path to pwd
    realpwd = os.path.realpath(os.getenv('PWD'))
    if os.path.isabs(symlinkpath):
        newhome = os.path.normpath(os.path.join(realpwd, symlinkpath))
        symtarg_relpath = os.path.relpath(newhome, os.path.dirname(oldhome))
    else:
        newhome = os.path.normpath(os.path.join(realpwd, symlinkpath))
        symtarg_relpath = os.path.relpath(newhome, symlinkpath)
    retval['suggestion-relpath'] = symtarg_relpath

    # suggestion #3 - .userroot alternative
    try:
        rel_to_userroot = os.path.relpath(oldhome, get_userroot())
        symtarg_userroot = os.path.join('.userroot', rel_to_userroot)
    except FileNotFoundError:
        symtarg_userroot = ""
    retval['suggestion-userroot'] = symtarg_userroot

    return retval


def make_the_move(origlink, newlinkname, newtargetref, allowbroken=False, savebackup=False):
    # FIXME: put the imports at the top of the file
    from pathlib import Path
    import shutil
    backupname = newlinkname + "~"

    if Path(newtargetref).exists() or allowbroken:
        # TODO: make this atomic by creating and moving the new symlink over
        # the old one, rather than deleting then moving.
        if savebackup:
            if Path(backupname).exists():
                os.remove(backupname)
        if Path(newlinkname).is_symlink():
            if savebackup:
                os.rename(newlinkname, backupname)
                print("Backup {} saved.".format(backupname))
            else:
                os.remove(newlinkname)
        os.symlink(newtargetref, newlinkname)
    else:
        raise FileNotFoundError(newtargetref)
    retval = "{} -> {}".format(newlinkname, newtargetref)
    if not Path(newtargetref).exists():
        retval += "\nNOTE: {} doesn't appear to exist.".format(newtargetref)
    return retval


def main(argv=None):
    # using splitlines to just get the first line
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])

    parser.add_argument('-b', '--backup',
                        help='save a tilde backup of the edited symlink',
                        action="store_true")
    parser.add_argument('-j', '--just-print',
                        help='just print the JSON for debugging', action="store_true")
    parser.add_argument('-x', '--allow-broken',
                        help='allow resulting broken link', action="store_true")
    parser.add_argument('symlink', help='symlink for editing')
    args = parser.parse_args()

    try:
        oldvals = get_values_from_link(args.symlink)
    except OSError:
        print("File '{}' isn't a symlink.".format(args.symlink))
        parser.print_usage()
        sys.exit(1)

    oldvals['allowbroken'] = args.allow_broken
    oldvals['savebackup'] = args.backup
    newvals = symlink_ui_urwid.start_main_loop(oldvals)

    if args.just_print:
        import json
        if newvals == 'cancel':
            print(json.dumps(oldvals, indent=4))
        else:
            print(json.dumps(newvals, indent=4))
        sys.exit()

    origlink = oldvals['origlink']
    try:
        newtargetref = newvals['targetref']
        newlinkname = newvals['origlink']
    except TypeError:
        # newvals is a simple scalar on <Cancel>
        print("Cancelled edit. {} is unchanged.".format(origlink))
        sys.exit()
    try:
        status = make_the_move(origlink, newlinkname, newtargetref,
                               allowbroken=newvals['allowbroken'],
                               savebackup=newvals['savebackup'])
        print(status)
    except FileNotFoundError:
        print("File not found: " + newtargetref)
        print("'Allow writing broken symlink' set to '{}'.  Aborting.".format(
            newvals['allowbroken']))


if '__main__' == __name__:
    main()
