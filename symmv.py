#!/usr/bin/env python

import os
import shutil
import argparse

def symmv(src, dst):
    if os.path.islink(src):
        linkto = os.readlink(src)
        os.symlink(linkto, dst)
    else:
        shutil.move(src, dst)
        os.symlink(dst, src)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='mv a file from src to dst, then symlink src to dst' ) 
    parser.add_argument('src', help='original file')
    parser.add_argument('dst', help='place to move')
    return parser.parse_args()

def main():
    args = parse_arguments()
    symmv(args.src, args.dst)

if __name__ == "__main__":
    main()
