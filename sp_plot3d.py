#!/usr/bin/env python3

import sys
import os
import re
import spectrum as sp
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
import numpy as np


# Collect data from files
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

zs = []
verts = []
counter = 1
for spctr in data:
    fname = spctr.headers['filepath']
    try:
        print(fname)
        radius = re.search(
            'R(\d+(\.\d+)?)', os.path.basename(fname)).groups()[0]
        # print(float(re.findall('_R\d\d_', fname)[0].replace('_','').replace('R','')))
        # zs.append(float(re.findall('_R\d\d_', fname)[0].replace('_','').replace('R','')))
        print(radius)
        zs.append(radius)
    except IndexError:
        zs.append(counter)
    print(zs)
    counter += 1
    verts.append(list(zip(spctr.x, spctr.y)))

cc = lambda arg: colorConverter.to_rgba(arg, alpha=0.3)
poly = PolyCollection(verts, facecolors=[cc('r'), cc('g'), cc('b'), cc('y')])
poly.set_alpha(0.7)

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.add_collection3d(poly, zs=zs, zdir='y')

ax.set_xlabel('Energy, eV')
# ax.set_xlim3d(0, 10)
ax.set_ylabel('Signal')
# ax.set_ylim3d(-1, 4)
ax.set_zlabel('Radius, nm')
# ax.set_zlim3d(0, 1)

plt.show()


# xs = np.arange(0, 10, 0.4)
# verts = []
# zs = [0.0, 1.0, 2.0, 3.0]
# for z in zs:
#     ys = np.random.rand(len(xs))
#     ys[0], ys[-1] = 0, 0
#     verts.append(list(zip(xs, ys)))
#
# poly = PolyCollection(verts, facecolors = [cc('r'), cc('g'), cc('b'),
#                                            cc('y')])
# poly.set_alpha(0.7)
# ax.add_collection3d(poly, zs=zs, zdir='y')
#
# ax.set_xlabel('X')
# ax.set_xlim3d(0, 10)
# ax.set_ylabel('Y')
# ax.set_ylim3d(-1, 4)
# ax.set_zlabel('Z')
# ax.set_zlim3d(0, 1)
#
# plt.show()


# TODO Make both nm and eV scales in one axes or two subplots or choose this as an option
# TODO Improve curves colors (e.g. gradients to guide the eye)
# legend = []
# for spdata in data:
#     pl.plot(spdata.x, spdata.y)
#     legend.append(os.path.basename(spdata.headers['filepath']))
# pl.grid()
# pl.legend(legend)
# pl.show()
#
