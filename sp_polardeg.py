#!/usr/bin/env python3

import sys
import os

import spectrum as sp

newfmt = "%s__TEdeg__%s"
usagefmt = "usage: {0} TEfile1 TMfile1 TEfile2 TMfile2"

_, first, datalist = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=2)
if first.__class__ is sp.Spectrum:
    datalist = [first] + datalist

while datalist:
    print('\n'.join([str(s.headers) for s in datalist]))
    sp1 = datalist.pop()
    # TODO check whether we found TE or TM, find the opposite and make the calculation
