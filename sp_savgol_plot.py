#!/usr/bin/env python3

# import argparse
import sys
import os
import matplotlib.pyplot as pl
import scipy.signal as sig
import spectrum as sp


if len(sys.argv) < 4:
    print("usage: {0} window_size poly_order datafile".format(
        os.path.basename(sys.argv[0])))
    sys.exit(0)


window_size = float(sys.argv[1])
poly_order = float(sys.argv[2])

datafile = sys.argv[3]
if not (os.path.exists(datafile) and os.path.isfile(datafile)):
    exit(1)
spec = sp.spectrum_from_file(datafile)

pl.figure()
legend = []
# TODO make both nm and eV scales in one axes or two subplots
yf = sig.savgol_filter(spec.y, window_size, poly_order)
pl.plot(spec.x, yf)
legend.append("Smoothed")

pl.plot(spec.x, spec.y)
legend.append(os.path.basename(spec.headers['filepath']))

pl.grid()
pl.legend(legend)
pl.show()
