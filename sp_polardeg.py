#!/usr/bin/env python3

import sys
import os

import spectrum as sp

newfmt = "%s__TEdeg__%s"
usagefmt = "usage: {0} TEfile1 TMfile1 [TEfile2 TMfile2 ... ]"

_, first, datalist = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=2)
if first.__class__ is sp.Spectrum:
    datalist = [first] + datalist

str_te, str_tm = 'te', 'tm'
te, tm = None, None

def search_pol(datalist, polstr):
    pass

while datalist:
    print('\n'.join([str(s.headers) for s in datalist]))
    spec = datalist.pop()
    spfname = spec.headers['filename']
    if str_te in spfname.lower():
        te = spec
        tm = search_pol(datalist, 'tm')
    elif str_tm in spfname.lower():
        tm = spec
        te = search_pol(datalist, 'te')

    if te is None or tm is None:
        print("WTF no pair found for " + spfname)
        continue

    poldeg = (tm - te) / (tm + te)

    # fpath_new = os.path.join(fdir, newfmt % (fname, ref_fname))
    # with open(fpath_new, 'w') as new_file:
    #     new_file.write(str(new_spec))
