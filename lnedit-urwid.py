#!/usr/bin/env python3
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


def get_values_from_link(linkfile, allowbroken, savebackup):
    """
    Read a symlink at the given linkfile, and return a dict for passing
    into the UI.
    """

    retval = {}
    # first add the core data:

    retval['origlink'] = linkfile
    symlinkvalue = os.readlink(linkfile)
    retval['targetref'] = symlinkvalue

    # suggestion #1 - absolute path
    abspath = os.path.realpath(linkfile)
    retval['suggestion-abspath'] = abspath

    # suggestion #2 - relative path to linkfile location
    realpwd = os.path.realpath(os.getenv('PWD'))
    if os.path.isabs(symlinkvalue):
        newhome = os.path.normpath(os.path.join(realpwd, symlinkvalue))
        abspath_dir = os.path.dirname(abspath)
        symtarg_relpath = os.path.relpath(newhome, abspath_dir)
    else:
        newhome = os.path.normpath(os.path.join(realpwd, symlinkvalue))
        linkvalpwd = os.path.join(realpwd, os.path.dirname(linkfile))
        symtarg_relpath = os.path.relpath(abspath, linkvalpwd)
    retval['suggestion-relpath'] = symtarg_relpath

    # suggestion #3 - .userroot alternative
    try:
        rel_to_userroot = os.path.relpath(abspath, get_userroot())
        symtarg_userroot = os.path.join('.userroot', rel_to_userroot)
    except FileNotFoundError:
        symtarg_userroot = ""
    retval['suggestion-userroot'] = symtarg_userroot

    # add parameters that were passed in
    retval['allowbroken'] = allowbroken
    retval['savebackup'] = savebackup

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


def get_vals_json(oldvals, newvals):
    import json
    if newvals == 'cancel':
        retval = json.dumps(oldvals, indent=4)
    else:
        retval = json.dumps(newvals, indent=4)
    return retval


def main(argv=None):
    # using splitlines to just get the first line
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])

    # 0. fetch commandline args
    parser.add_argument('-b', '--backup',
                        help='save a tilde backup of the edited symlink',
                        action="store_true")
    parser.add_argument('-f', '--force',
                        help='Write the symlink even if it\'s broken', action="store_true")
    parser.add_argument('-j', '--just-print',
                        help='just print the JSON for debugging', action="store_true")
    parser.add_argument('symlink', help='symlink for editing')
    args = parser.parse_args()

    # 1. get oldvals from symlink given on cli
    try:
        oldvals = get_values_from_link(args.symlink,
                                       allowbroken=args.force,
                                       savebackup=args.backup)
    except OSError:
        print("File '{}' isn't a symlink.".format(args.symlink))
        parser.print_usage()
        sys.exit(1)

    # 2. get newvals from user interface
    newvals = symlink_ui_urwid.start_main_loop(oldvals)

    # 3. just print if that was what was instructed on the cli
    if args.just_print:
        print(get_vals_json(oldvals, newvals))
        sys.exit()

    origlink = oldvals['origlink']

    # 4. otherwise perform some hacky exception handling
    try:
        newtargetref = newvals['targetref']
        newlinkname = newvals['origlink']
    except TypeError:
        # newvals is a simple scalar on <Cancel>
        print("Cancelled edit. {} is unchanged.".format(origlink))
        sys.exit()

    # 5. And maybe even try more hacky exception handling
    try:
        status = make_the_move(origlink, newlinkname, newtargetref,
                               allowbroken=newvals['allowbroken'],
                               savebackup=newvals['savebackup'])
        print(status)
    except FileNotFoundError:
        print("File not found: " + newtargetref)
        print("'Allow writing broken symlink' set to '{}'.  Aborting.".format(
            newvals['allowbroken']))

    # 6. Delete the original link if it was renamed (and the user allows)
    if newvals['deleteorig'] and origlink != newlinkname:
        print('Replacing %s with %s' % (origlink, newlinkname))
        from pathlib import Path
        Path(origlink).unlink()


if '__main__' == __name__:
    main()
