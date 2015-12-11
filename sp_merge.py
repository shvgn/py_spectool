#!/usr/bin/env python3

import sys
import os
import re

import spectrum as sp


usagefmt = "usage: {0} file1 file2 [file3 ... ]"


def check_and_exit(data):
    """Check whether the argument is Spectrum instance and exit otherwise"""
    if not data.__class__ is sp.Spectrum:
        print("All arguments must be XY data, but this is not one: {0}".format(data))
        sys.exit(1)


_, merged, datalist = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=2)
check_and_exit(merged)

# Controllers
l = len(datalist) + 1
counter = 0

while datalist:
    spec = datalist.pop(0)
    check_and_exit(spec)
    try:
        merged = merged.merge(spec)
    except ValeError:
        datalist.append(spec)
        continue
    counter += 1
    if counter > l*(l-1)/2:
        print("Some data cannot be merged with others. We've tried enough:")
        print('\n'.join(['\t' + s.headers['filepath'] for s in datalist]))
        sys.exit(1)

fdir, fname = os.path.split(merged.headers['filepath'])
# FIXME add suffix manipulation functions
newpath = os.path.join(fdir, 'merged_' + fname)
# try-catch on writing?
with open(newpath, 'w') as newfile:
    newfile.write(str(merged))
