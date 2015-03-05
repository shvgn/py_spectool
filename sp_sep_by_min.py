#!/usr/bin/env python3

__author__ = 'Evgenii Shevchenko'
__email__ = 'shevchenko@beam.ioffe.ru'
__date__ = '2015-02-11'

import sys
import os
import numpy as np
import spectrum as sp

DIVIDER = 2.5
SHIFT_TO_MIN = 10  # Indexes
 
if len(sys.argv) == 1:
    print("usage: {0} [datafile2 ...]".format(
        os.path.basename(sys.argv[0])))
    sys.exit(0)

data = []
for arg in sys.argv[1:]:
    if not (os.path.exists(arg) and os.path.isfile(arg)):
        print("Warning! Cannot open file <" + arg + ">. Skipping.")
        continue
    data.append(sp.spectrum_from_file(arg))

for spdata in data:
    l = len(spdata.y)

    # print(l // DIVIDER)
    # print(l - l // DIVIDER)
    # print(spdata.y[l // DIVIDER: l - l // DIVIDER])

    # l_offset = l // DIVIDER
    # r_offset = l - l_offset

    l_offset = np.argmax(spdata.y[:l // 2])
    r_offset = np.argmax(spdata.y[l // 2:]) + l // 2
    minpos = np.argmin(spdata.y[l_offset:r_offset + 1]) + l_offset

    while minpos == l_offset:
        l_offset -= SHIFT_TO_MIN
        r_offset = l - l_offset
        minpos = np.argmin(spdata.y[l_offset:r_offset + 1]) + l_offset
    while minpos == r_offset:
        r_offset += SHIFT_TO_MIN
        l_offset = l - r_offset
        minpos = np.argmin(spdata.y[l_offset:r_offset + 1]) + l_offset

    # print("Length is ", l, "Minpos is ", minpos)

    # QW is on the left and barrier is on the right if x is in eV's
    x_qw = spdata.x[0:minpos]
    y_qw = spdata.y[0:minpos]

    x_br = spdata.x[minpos:l]
    y_br = spdata.y[minpos:l]

    if np.mean(spdata.x) > 100:
        # It's nanometers, not electron-volts
        x_qw, x_br = x_br, x_qw
        y_qw, y_br = y_br, y_qw
    qw = sp.Spectrum(x_qw, y_qw, spdata.headers.copy())
    br = sp.Spectrum(x_br, y_br, spdata.headers.copy())

    qw.headers['filepath'] += "__qw"
    br.headers['filepath'] += "__br"

    with open(qw.headers['filepath'], 'w') as new_file:
        new_file.write(str(qw))
    with open(br.headers['filepath'], 'w') as new_file:
        new_file.write(str(br))
