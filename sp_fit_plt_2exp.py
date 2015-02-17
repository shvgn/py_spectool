#!/usr/bin/env python3
# This program fits the thermal PL quenching
# double exponential function and shows the plot
# Tha aim is to get activation energies

__author__ = 'Evgenii Shevchenko'
__email__ = 'shevchenko@beam.ioffe.ru'
__date__ = '2015-02-17'

import sys
import os

import matplotlib.pyplot as pl
import numpy as np
from scipy.optimize import curve_fit

import spectrum as sp



# TIME_PERIOD = 13.158  # nanoseconds
# ITERATIONS_NUMBER = 300
# INDEX_LENGTH_AFTER_MAX = 10
# INDEX_OF_GOOD_CURVE_START = 250
CONST_BOLZMANN = 8.6173324e-5  # eV / K


def fitfun(t, t0, c1, c2, e1, e2):
    """
    Double exponent thermal PL quenching
    I = fitfun(t, t0, c1, c2, e1, e2) =
      =  (1 + c1 * np.exp(-e1 / (CONST_BOLZMANN * (t - t0))) + c2 * np.exp(-e2 / (CONST_BOLZMANN * (t - t0)))) ** -1
    """
    return (1 + c1 * np.exp(-e1 / (CONST_BOLZMANN * (t - t0))) + c2 * np.exp(-e2 / (CONST_BOLZMANN * (t - t0)))) ** -1


def fitfun_f(t0):
    """
    Double exponent thermal PL quenching closure with defined t and t0
    I = fitfun_f(t, t0) -> fitfun(c1, c2, e1, e2)
    """
    return lambda t, c1, c2, e1, e2: fitfun(t, t0, c1, c2, e1, e2)


if len(sys.argv) < 2:
    print("usage: {0} datafile1 [datafile2... ]".format(
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

print("Filename\t\tc1\t\tc2\t\te1\t\te2")

initial_params = (180., 5., 0.04, 0.01)
for spec in data:

    maxidx = np.argmax(spec.y)
    spec = spec / np.max(spec.y)  # Normalize by Y maximum
    if maxidx < 15:
        maxidx = 15
        spec = spec / spec.y[maxidx]

    t0 = spec.x[maxidx]

    xfit = spec.x[maxidx:len(spec)]
    yfit = spec.x[maxidx:len(spec)]

    try:
        params, conv = curve_fit(fitfun_f(t0), xfit, yfit, p0=initial_params)
        print(conv)
    except RuntimeError:
        # print("Couldn't find optimal parameters.")
        print(spec.headers['filepath'], "\t-\t-\t-\t-")
        continue

    # Parameters are in order [c1, c2, e1, e2]
    fmt = "\t%f\t%f\t%f\t%f"
    print(spec.headers['filepath'], fmt % tuple(params))
    # print(spec.headers['filepath'], params)

    # Fitted sum of stretched exponents
    pl.plot(1 / xfit, fitfun(xfit, t0, *params))
    # pl.semilogy(1 / xfit, fitfun(xfit, t0, *params))
    legend.append("Fitting [c1=%.2f, c2=%.2f, e1=%.2f, e2=%.2f]" % tuple(params))

    # Initial params
    pl.plot(xfit, fitfun(xfit, t0, *initial_params))
    # pl.semilogy(1 / xfit, fitfun(xfit, t0, *initial_params))
    legend.append("Initial [c1=%.2f, c2=%.2f, e1=%.2f, e2=%.2f]" % tuple(initial_params))

    # Original data
    pl.plot(spec.x, spec.y)
    # pl.semilogy(1 / spec.x, spec.y)
    legend.append(os.path.basename(spec.headers['filepath']))

pl.grid()
pl.legend(legend)
pl.show()
