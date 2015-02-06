#!/usr/bin/env python3

# import argparse
import sys
import os
import matplotlib.pyplot as pl
import spectrum as sp
import numpy as np


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

pl.figure()
# TODO show grid
# TODO generate legend
# TODO make both nm and eV scales in one axes or two subplots
legend = []
legendd = []
legenddd = []
for spdata in data:
    pl.subplot(311)
    pl.plot(spdata.x, spdata.y)
    legend.append(os.path.basename(spdata.headers['filepath']))

    pl.subplot(312)
    # dx, dy = sp.ary_deriv(spdata.x, spdata.y) # Better way
    dy = [sp.point_deriv(spdata.x, spdata.y, i)
          for i in range(1, len(spdata.y) - 1)]
    pl.plot(spdata.x[1:len(spdata.x) - 1], np.abs(dy))
    legendd.append(os.path.basename(spdata.headers['filepath']))

    pl.subplot(313)
    ddy = [sp.point_deriv(spdata.x[1:len(spdata.x) - 1], dy, i)
           for i in range(1, len(dy) - 1)]
    pl.plot(spdata.x[2:len(spdata.x) - 2], np.abs(ddy))
    legenddd.append(os.path.basename(spdata.headers['filepath']))

pl.subplot(311)
pl.grid()
pl.legend(legend)

pl.subplot(312)
pl.grid()
pl.legend(legendd)

pl.subplot(313)
pl.grid()
pl.legend(legenddd)

pl.show()
