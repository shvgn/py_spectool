#!/usr/bin/env python3

import sys
import os
import spectrum as sp

usagefmt = "usage: {0} file1 [file2 ... ]"

_, refdata, data = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=1)
data = [refdata] + data

for spdata in data:
    sp.check_and_exit(spdata)
    print( ("%.6f" % spdata.area()).rjust(15), "  ", spdata.headers['filepath'])
