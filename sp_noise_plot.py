#!/usr/bin/env python3

# import argparse
import sys
import os
import matplotlib.pyplot as pl
import spectrum as sp


newfmt = "%s__sub__%s"

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
    print(spdata.headers['filepath'], "\t", spdata.y_shift())
    pl.figure()
    legend = []
    ynoise = spdata.y_shift()
    pl.plot([spdata.x[0], spdata.x[len(spdata.x) - 1]], [ynoise, ynoise])
    legend.append("Y shift = " + str(ynoise))
    pl.plot(spdata.x, spdata.y)
    legend.append(os.path.basename(spdata.headers['filepath']))
    pl.grid()
    pl.legend(legend)
    pl.show()
