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

# TODO Make both nm and eV scales in one axes or two subplots or choose this as an option
# TODO Improve curves colors (e.g. gradients to guide the eye)
legend = []
for spdata in data:
    pl.plot(spdata.x, spdata.y)
    legend.append(os.path.basename(spdata.headers['filepath']))
pl.grid()
pl.legend(legend)
pl.show()

