#!/usr/bin/env python3

# import argparse
import sys
import os

import spectrum as sp


# TODO
# We have two options here for X which are nanometers or electron-volts. Thus
# the operation must be independent from X units.

newfmt = "%s__add__%s"

if len(sys.argv) == 1:
    print("usage: {0} adder_file datafile1 [datafile2 ...]".format(
        os.path.basename(sys.argv[0])))
    sys.exit(0)

refdata = sp.get_ref_data(sys.argv[1])
data = []
for arg in sys.argv[2:]:
    if not (os.path.exists(arg) and os.path.isfile(arg)):
        print("Warning! Cannot open file <" + arg + ">. Skipping.")
        continue
    data.append(sp.spectrum_from_file(arg))

if refdata.__class__ == sp.Spectrum:
    ref_fname = os.path.basename(refdata.headers['filepath'])
else:
    ref_fname = str(refdata)

for spdata in data:
    new_spec = spdata + refdata
    fname = os.path.basename(spdata.headers['filepath'])
    fdir = os.path.dirname(spdata.headers['filepath'])
    fpath_new = os.path.join(fdir, newfmt % (fname, ref_fname))
    with open(fpath_new, 'w') as new_file:
        new_file.write(str(new_spec))
