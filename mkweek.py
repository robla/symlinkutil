#!/usr/bin/env python3
# mkweek
# This program takes a date on the command line, and builds out week-
# based directories correlating with the given date.
# As of this writing on 2017-04-24, there are hard-coded directories:
# /home/robla/YYYY - these are where the stuff I hope to keep around
# permanently hangs around.
# /home/robla/tmp - week-based directories are built in here, with the
#  assumption that if it gets too cluttered or full, I'll nuke the 
#  directories
import argparse
import datetime
import isoweek
import os
import re

# Use argparse to parse the command-line arguments:
def parse_arguments():
    parser = argparse.ArgumentParser(
        description='make week-based directories')
    parser.add_argument(
        'date', nargs='?',
        help='iso date (default today)',
        default=datetime.date.today().isoformat())
    parser.add_argument('--verbose', '-v', action='store_true')
    return parser.parse_args()


# parse out weeks given in iso format (e.g. "17W17" or "2017W17")
def parseweek(datestr):
    yearweek = re.search(r'(\d{2})W(\d{2})', datestr)
    thisyear = int("20" + yearweek.group(1))
    thisweek = int(yearweek.group(2))
    return isoweek.Week(thisyear, thisweek)


# make directories for a given week, given a pathfmt
def mkweek(pathfmt, thisdate, verbose=False):
    thisdatepath = thisdate.strftime(pathfmt)
    if verbose: print('Doing ' + thisdate.strftime(pathfmt))
    try:
        os.makedirs(thisdate.strftime(pathfmt))
    except FileExistsError:
        pass
    lastweek = thisdate - datetime.timedelta(days=7)
    if verbose: print(lastweek.strftime(pathfmt))
    try:
        os.symlink(lastweek.strftime(pathfmt),
            os.path.join(thisdatepath, 'lastweek'))
    except FileExistsError:
        pass
    nextweek = thisdate + datetime.timedelta(days=7)
    try:
        os.symlink(nextweek.strftime(pathfmt),
            os.path.join(thisdatepath, 'nextweek'))
    except FileExistsError:
        pass
    if verbose: print(nextweek.strftime(pathfmt))


# Wrapper around mkweek() that deals with temp and permanent directory
# logic
def mkweek_full(thisdate, mktemp=True, mkperm=True, verbose=False):
    tempdir='/home/robla/tmp'
    tempfmt=os.path.join(tempdir, "%G", "%gW%V")
    permdir='/home/robla'
    permfmt=os.path.join(permdir, "%G", "%gW%V")

    if(mktemp):
        thisdatepath = thisdate.strftime(tempfmt)
        mkweek(tempfmt, thisdate, verbose)
        try:
            # link from the tmp dir to the perm
            os.symlink(thisdate.strftime(permfmt),
                os.path.join(thisdatepath, 'perm'))
        except FileExistsError:
            pass

    if(mkperm):
        thisdatepath = thisdate.strftime(permfmt)
        mkweek(permfmt, thisdate, verbose)
        try:
            # link from the perm dir to the tmp
            os.symlink(thisdate.strftime(tempfmt),
                os.path.join(thisdatepath, 'tmp'))
        except FileExistsError:
            pass


def main():
    args = parse_arguments()
    datestr = args.date

    if(re.search(r'\d{4}-\d{2}-\d{2}', datestr)):
        thisdate = datetime.datetime.strptime(datestr, '%Y-%m-%d').date()
    elif(re.search(r'\d{2}W\d{2}', datestr)):
        thisweek = parseweek(datestr)
        thisdate = thisweek.monday()
    else:
        thisdate = datetime.datetime.now()
    mkweek_full(thisdate, mktemp=True, mkperm=True,
        verbose=args.verbose)


if __name__ == "__main__":
    main()

