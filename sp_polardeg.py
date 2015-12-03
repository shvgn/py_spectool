#!/usr/bin/env python3

import sys
import os
import re

import spectrum as sp


def te_or_tm(matchobj):
    '''Returns 'te' for 'tm' and vice versa. Used in re.sub for polarization
    type substitution'''
    if matchobj.group(0) == 'te':
        return 'tm'
    elif matchobj.group(0) == 'tm':
        return 'te'
    else:
        raise ValueError("Invalid polarization: '" + matchobj.group(0) + "'")


usagefmt = "usage: {0} TEfile1 TMfile1 [TEfile2 TMfile2 ... ]"

_, first, datalist = sp.get_data_list(sys.argv, usagefmt=usagefmt, minfiles=2)
if first.__class__ is sp.Spectrum:
    datalist = [first] + datalist

# Pattern for polarization search in a path
tetm = re.compile(".*\\" + os.path.sep + '.*(te|tm).*')
polchooser = lambda m: m.groups(0)[0].lower() == 'te' and 'tm' or 'te'


def extract_pair(datalist):
    """Returns spectrum instances for two corresponding TE and TM polarizations
    searched by their filenames"""
    str_te, str_tm = 'te', 'tm'
    te, tm = None, None

    data1 = datalist.pop()
    path1 = data1.headers['filepath']
    fdir, fname1 = os.path.split(path1)
    fname2 = re.sub('(TE|TM)', polchooser, fname1, flags=re.IGNORECASE)
    if fname1 == fname2:
        raise Exception("Cannot determine polarization from name {0}".format(fname1))
    path2 = os.path.join(fdir, fname2)
    data2 = [d for d in datalist if d.headers['filepath'].lower() == path2.lower()]
    
    # print('Got', data1.headers['filepath'])
    # print('Looking for', path2)
    l = len(data2) 
    if l == 1:
        data2 = data2[0]
        # print('Found', data2.headers['filepath'])
        datalist.remove(data2)
    elif l == 0:
        raise Exception('{0} not found'.format(path2))
    else:
        raise Exception('Found {0} corresponding files for {1}:\n{2}'.format( 
                l, path1, '\t\n'.join([d.headers['filepath'] for d in data2])))

    if str_te in fname1.lower():
        te, tm = data1, data2
    elif str_tm in fname1.lower():
        te, tm = data2, data1
    return te, tm


while datalist:
    # Debug
    # print('\n'.join([str(s.headers) for s in datalist]))
    try:  # Stupid pattern?
        te, tm = extract_pair(datalist)
    except Exception as e:
        print("Error: {0}".format(e))
        continue

    poldeg = (tm - te) / (tm + te)
    print(poldeg.headers)

    fdir, fname_te = os.path.split(te.headers['filepath'])
    fname = re.sub('TE', 'TM-TE', fname_te, flags=re.IGNORECASE)
    newpath = os.path.join(fdir, fname)
    # try-catch on writing?
    with open(newpath, 'w') as newfile:
        newfile.write(str(poldeg))
