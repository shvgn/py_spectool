#!/usr/bin/env python3

# import argparse
import sys
import os

import matplotlib.pyplot as pl

import spectrum as sp


if len(sys.argv) == 1:
    print("usage: {0} datafile1 [datafile2 ...]".format(os.path.basename(sys.argv[0])))
    sys.exit(0)

data = []
for arg in sys.argv[1:]:
    if not (os.path.exists(arg) and os.path.isfile(arg)):
        print("Warning! Cannot open file <" + arg + ">. Skipping.")
        continue
    data.append(sp.spectrum_from_file(arg))

pl.figure()
for spdata in data:
    pl.plot(spdata.x, spdata.y)
pl.show()

