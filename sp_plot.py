#!/usr/bin/env python3

# TODO make both nm and eV scales in one axes or two subplots

import sys
import os
import re

import matplotlib.pyplot as pl

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

pl.figure()
legend = []
for spdata in data:
    # Get rid of metainfo after kelvins, only which matters in plots
    legend_item = re.sub(
        "K.*", " K", os.path.basename(spdata.headers['filepath']))
    # Get rid of useless prefix in legend
    legend_item = legend_item.replace("ev-", "")
    if len(legend_item) > 10:
        # Only first ten characters. We unlikely need more.
        legend.append(legend_item[0:10] + "...")
    else:
        legend.append(legend_item)
    pl.plot(spdata.x, spdata.y, label=legend_item)
pl.grid()
pl.legend(legend)
pl.show()
