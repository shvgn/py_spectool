#!/usr/bin/env python3

__author__ = 'Evgenii Shevchenko'
__email__ = 'shevchenko@beam.ioffe.ru'
__date__ = '2015-02-11'

import sys
import os

import spectrum as sp

if len(sys.argv) < 4:
    print("usage: {0} xleft xright [datafile ...]".format(
        os.path.basename(sys.argv[0])))
    print("xleft or xright can be omitted by passing underscore '_'")
    sys.exit(0)


# Check the boundaries
xleft_str = sys.argv[1]
xright_str = sys.argv[2]

if xleft_str == "_":
    xleft = None
else:
    xleft = float(xleft_str)

if xright_str == "_":
    xright = None
else:
    xright = float(xright_str)

if xleft is None and xright is None:
    sys.exit(0)

# Collecting data
data = []
for arg in sys.argv[3:]:
    if not (os.path.exists(arg) and os.path.isfile(arg)):
        print("Warning! Cannot open file <" + arg + ">. Skipping.")
        continue
    data.append(sp.spectrum_from_file(arg))

dl = len(data)
lenstr = str(len(data))
ident = 2 * len(lenstr) + 1
cnt = 1

for spdata in data:
    if dl > 1:
        print(("%s/%s" % (str(cnt), lenstr)).rjust(ident), "  ", end='')
        print("Splitting %s" % spdata.headers['filepath'])
    cnt += 1

    xmin, ymin, minpos = spdata.min(xleft, xright)
    print("".rjust(ident) + "  minpos = %d   xmin = %f   ymin = %f" % (minpos, xmin, ymin))

    l = len(spdata)
    if minpos > 0:
        spleft = sp.Spectrum(spdata.x[0:minpos], spdata.y[0:minpos], spdata.headers.copy())
        spleft.headers['filepath'] += "__left(to_%s)" % str(xmin)
        with open(spleft.headers['filepath'], 'w') as new_file:
            new_file.write(str(spleft))
    else:
        print("".rjust(ident) + "  Left-side spectrum is empty, omitting.")

    if minpos < l - 1:
        spright = sp.Spectrum(spdata.x[minpos:l], spdata.y[minpos:l], spdata.headers.copy())
        spright.headers['filepath'] += "__right(from_%s)" % str(xmin)
        with open(spright.headers['filepath'], 'w') as new_file:
            new_file.write(str(spright))
    else:
        print("".rjust(ident) + "  Right-side spectrum is empty, omitting.")
