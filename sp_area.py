#!/usr/bin/env python3

import sys
import os
import spectrum as sp

if len(sys.argv) == 1:
    print("usage: {0} datafile1 [datafile2 ...]".format(
        os.path.basename(sys.argv[0])))
    sys.exit(0)

data = []
for arg in sys.argv[1:]:
    if not (os.path.exists(arg) and os.path.isfile(arg)):
        print("Warning! Cannot open file <" + arg + ">. Skipping.")
        continue
    data.append(sp.spectrum_from_file(arg))

for spdata in data:
    print( ("%.6f" % spdata.area()).rjust(15), "  ", spdata.headers['filepath'])
    # print(str(spdata.area()).rjust(15), "  ", spdata.headers['filepath'])

