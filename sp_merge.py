#!/usr/bin/env python3

import sys
import os
import re

import spectrum as sp


usagefmt = "usage: {0} file1 file2 [file3 ... ]"
newfmt = 'merged_{0}'

_, merged, data = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=2)
sp.check_and_exit(merged)

# Controllers
l = len(data) + 1
counter = 0
enough = l*(l-1)/2

while data:
    spec = data.pop(0)
    sp.check_and_exit(spec)
    try:
        merged.merge(spec)
    except ValueError:
        data.append(spec)
        continue
    counter += 1
    if counter > enough:
        print("Some data cannot be merged with others. We've tried enough:")
        print('\n'.join(['\t' + s.headers['filepath'] for s in data]))
        sys.exit(1)

fdir, fname = os.path.split(merged.headers['filepath'])
# TODO add suffix manipulation?
newpath = os.path.join(fdir, newfmt.format(fname))
with open(newpath, 'w') as newfile:
    newfile.write(str(merged))
