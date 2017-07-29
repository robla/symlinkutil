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


def parse_arguments():
    """ see http://docs.python.org/library/argparse """
    parser = argparse.ArgumentParser(
        description='Make pwd the symlink target, symlinking the old target back')
    parser.add_argument('-f', '--force',
                    help='force the action without confirming',
                    action="store_true")
    return parser.parse_args()


def swapln(oldhome, newhome, forsure=False):
    print("rm {}".format(newhome))
    print("mv {} {}".format(oldhome, newhome))
    print("ln -rs {} {} #I think....".format(newhome, oldhome))
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

    args = parse_arguments()
    oldhome = os.getcwd()
    newhome = os.getenv('PWD')

    print('oldhome: {} newhome: {}'.format(oldhome, newhome))

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
