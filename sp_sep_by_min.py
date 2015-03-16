#!/usr/bin/env python3

__author__ = 'Evgenii Shevchenko'
__email__ = 'shevchenko@beam.ioffe.ru'
__date__ = '2015-02-11'

import sys
import os
import numpy as np
import spectrum as sp

if len(sys.argv) < 4:
    print("usage: {0} xleft xright [datafile ...]".format(
        os.path.basename(sys.argv[0])))
    print("xleft or xright can be omitted by passing underscore '_'")
    sys.exit(0)


# Check the boundaries
xleft_str  = sys.argv[1]
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



# 
# DIVIDER = 2.5
# SHIFT_TO_MIN = 10  # Indexes
#  
# if len(sys.argv) == 1:
#     print("usage: {0} [datafile2 ...]".format(
#         os.path.basename(sys.argv[0])))
#     sys.exit(0)
# 


# Filename suffix format 
# fmt = "__cut"
# suffix = ""
# if xleft is None:
#     fmt += "[:,%s]"
#     suffix = fmt % xright_str
# elif xright is None:  
#     fmt += "[%s,:]"
#     suffix = fmt % xleft_str
# else:
#     fmt += "[%s,%s]"
#     suffix = fmt % (xleft_str, xright_str)
# 

# Collecting data
data = []
for arg in sys.argv[3:]:
    if not (os.path.exists(arg) and os.path.isfile(arg)):
        print("Warning! Cannot open file <" + arg + ">. Skipping.")
        continue
    data.append(sp.spectrum_from_file(arg))

# Processing
for spdata in data:
    (xmin, ymin, minpos) = spdata.min(xleft, xright)
    l = len(spdata)
    print("minpos " + str(minpos))
    print("xmin" + str(xmin))
    print("ymin" + str(ymin))
    spleft  = sp.Spectrum( spdata.x[0:minpos], spdata.y[0:minpos], spdata.headers.copy() )
    spright = sp.Spectrum( spdata.x[minpos:l], spdata.y[minpos:l], spdata.headers.copy() )

    spleft.headers['filepath']  += "__left(to_%s)" % str(xmin)
    spright.headers['filepath'] += "__right(from_%s)" % str(xmin)

    with open(spleft.headers['filepath'], 'w') as new_file:
        new_file.write(str(spleft))
    with open(spright.headers['filepath'], 'w') as new_file:
        new_file.write(str(spright))

