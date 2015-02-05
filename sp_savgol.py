#!/usr/bin/env python3

# import argparse
import sys
import os
import scipy.signal as sig
import spectrum as sp


newfmt = "%s__savgol_%d_%d"

if len(sys.argv) == 1:
    print("usage: {0} window_size poly_order datafile1 [datafile2 ...]"\
        .format(os.path.basename(sys.argv[0])))
    sys.exit(0)

# refdata = sp.get_ref_data(sys.argv[1])
window_size = float(sys.argv[1])
poly_order = float(sys.argv[2])

data = []
for arg in sys.argv[3:]:
    if not (os.path.exists(arg) and os.path.isfile(arg)):
        print("Warning! Cannot open file <" + arg + ">. Skipping.")
        continue
    data.append(sp.spectrum_from_file(arg))

for spdata in data:
    sm_headers = spdata.headers
    sm_headers["filter"] = "savgol, %d, %d" % (window_size, poly_order)
    sm_data = sp.Spectrum(spdata.x, \
        sig.savgol_filter(spdata.y, window_size, poly_order), sm_headers )

    fname = os.path.basename(spdata.headers['filepath'])
    fdir = os.path.dirname(spdata.headers['filepath'])
    fpath_new = os.path.join(fdir, newfmt % (fname, window_size, poly_order))
    with open(fpath_new, 'w') as new_file:
        new_file.write(str(sm_data))
