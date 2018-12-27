#!/usr/bin/env python3

import argparse
import os
import shutil
import sys


# adapted from http://stackoverflow.com/a/3042378/314034
def confirm_step(prompt):
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


def swapln(oldhome, newhome, forsure=False):
    print("rm (1-new)")
    print("  1-new) {}".format(newhome))
    print("mv (1-old) (2-new)")
    print("  1-old) {}".format(oldhome))
    print("  2-new) {}".format(newhome))
    print("ln -rs (1-new) (2-old)")
    print("  1-new) {}".format(newhome))
    print("  2-old) {}".format(oldhome))
    if forsure:
        print("okaaaaay....")
        os.remove(newhome)
        shutil.move(oldhome, newhome)
        # newsymtarg is what the new path looks like from the dir of
        # the old path
        newsymtarg = os.path.relpath(newhome, os.path.dirname(oldhome))
        os.symlink(newsymtarg, oldhome)
    else:
        print("haven't done it yet...")


def main(argv=None):
    """ Make PWD the symlink target, symlinking the old target back """

    parser = argparse.ArgumentParser(
        description='Make pwd the symlink target, symlinking the old target back')
    parser.add_argument('-f', '--force',
                    help='force the action without confirming',
                    action="store_true")
    args = parser.parse_args()

    oldhome = os.getcwd()
    newhome = os.getenv('PWD')

    print('oldhome: {}'.format(oldhome))
    print('newhome: {}'.format(newhome))

    if args.force:
        swapln(oldhome, newhome, forsure=True)
    else:
        swapln(oldhome, newhome)
        if confirm_step('wanna keep going?'):
            swapln(oldhome, newhome, forsure=True)
        else:
            print("well, nevermind then")


if __name__ == '__main__':
    exit_status = main(sys.argv)
    sys.exit(exit_status)
