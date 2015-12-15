#!/usr/bin/env python3

# import argparse
import sys
import os

import spectrum as sp

newfmt = "{0}__sub__{1}"
usagefmt = "usage: {0} file_or_num file1 [file2 ... ]"

ref_fname, refdata, data = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=2)

l = len(data)
ll = str(len(data))
ident = 2 * len(ll) + 1
cnt = 1

for spdata in data:
    if l > 1:
        print(("%s/%s" % (str(cnt), ll)).rjust(ident), "  ", end='')
    cnt += 1
    new_spec = spdata - refdata
    fname = os.path.basename(spdata.headers['filepath'])
    fdir = os.path.dirname(spdata.headers['filepath'])
    fpath_new = os.path.join(fdir, newfmt.format(fname, ref_fname))
    with open(fpath_new, 'w') as new_file:
        new_file.write(str(new_spec))
