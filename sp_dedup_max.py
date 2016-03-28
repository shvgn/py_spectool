#!/usr/bin/env python3

# import argparse
import sys
import os

import spectrum as sp


newfmt = "{0}__dedup"
usagefmt = "usage: {0} file1 file2 [file3 ... ]"

_, refdata, data = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=1)
data = [refdata] + data

for spdata in data:
    sp.check_and_exit(spdata)
    spdata.deduplicate(comparator=max)

    fname = os.path.basename(spdata.headers['filepath'])
    fdir  = os.path.dirname( spdata.headers['filepath'])
    new_path = os.path.join(fdir, newfmt.format(fname))
    
    with open(new_path, 'w') as new_file:
        new_file.write(str(spdata))
