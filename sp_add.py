#!/usr/bin/env python3

# import argparse
import sys
import os

import spectrum as sp


newfmt = "{0}__add__{1}"
usagefmt = "usage: {0} file1 file2 [file3 ... ]"

ref_fname, refdata, data = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=2)

l = len(data)  # Number of spectra in the data, say 23
ll = str(l)  # "23"
ident = 2 * len(ll) + 1  # 2*2+1 = 5, to have enough space for "XX/23"
cnt = 1

for spdata in data:
    if l > 1:
        print(("%s/%s" % (str(cnt), ll)).rjust(ident), "  ", end='')
    cnt += 1
    new_spec = spdata + refdata
    fname = os.path.basename(spdata.headers['filepath'])
    fdir = os.path.dirname(spdata.headers['filepath'])
    new_path = os.path.join(fdir, newfmt.format(fname, ref_fname))
    # new_spec.headers['filepath'] = new_path
    with open(new_path, 'w') as new_file:
        new_file.write(str(new_spec))
