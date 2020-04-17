#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
from os.path import realpath, normpath


def confirm_step(prompt):
    '''
    y/n prompt
    adapted from http://stackoverflow.com/a/3042378/314034
    '''
    # raw_input returns the empty string for "enter"
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])

    print(prompt)
    while True:
        choice = input().lower()
        if choice in yes:
           return True
        elif choice in no:
           return False
        else:
           sys.stdout.write("Please respond with 'yes' or 'no'")


def swapln(oldhome, newhome, forsure=False, relative=False):
    if relative:
        # symtarg should be the new path as seen from the dir of
        # the old path
        symtarg = os.path.relpath(newhome, os.path.dirname(oldhome))
    else:
        symtarg = os.path.abspath(newhome)
    print("rm (1-new)")
    print("  1-new) {}".format(newhome))
    print("mv (1-old) (2-new)")
    print("  1-old) {}".format(oldhome))
    print("  2-new) {}".format(newhome))
    print("cd (1-olddir)")
    print("  1-olddir) {}".format(os.path.dirname(oldhome)))
    print("ln -s (1-symtarg)")
    print("  1-symtarg) {}".format(symtarg))
    if forsure:
        print("okaaaaay....")
        os.remove(newhome)
        shutil.move(oldhome, newhome)
        os.symlink(symtarg, oldhome)
    else:
        print("haven't done it yet...")


def main(argv=None):
    """ Make PWD the symlink target, symlinking the old target back """

    parser = argparse.ArgumentParser(
        description='Make pwd the symlink target, symlinking the old target back')
    parser.add_argument('-f', '--force',
                    help='force the action without confirming',
                    action="store_true")
    parser.add_argument('-r', '--relative',
                        help='use relative links (default is absolute)',
                        action="store_true")
    parser.add_argument('symfile', help='optional symlink to swap',
                        nargs='?', default=None)
    args = parser.parse_args()

    if args.symfile:
        try:
            oldhome = realpath(os.readlink(args.symfile))
        except OSError:
            print("'{}' is not a valid symlink".format(args.symfile))
            sys.exit()
        realpwd = realpath(os.getenv('PWD'))
        newhome = normpath(os.path.join(realpwd, args.symfile))
    else:
        oldhome = os.getcwd()
        newhome = os.getenv('PWD')

    print('oldhome: {}'.format(oldhome))
    print('newhome: {}'.format(newhome))

    if args.force:
        swapln(oldhome, newhome, forsure=True, relative=args.relative)
    else:
        swapln(oldhome, newhome, relative=args.relative)
        if confirm_step('wanna keep going?'):
            swapln(oldhome, newhome, forsure=True, relative=args.relative)
        else:
            print("well, nevermind then")


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
