#!/usr/bin/env python3
# This program fits the time-resolved photoluminescence decay curve with
# stretched exponent and shows the plot

__author__ = 'Evgenii Shevchenko'
__email__ = 'shevchenko@beam.ioffe.ru'
__date__ = '2015-02-11'

import sys
import os

import matplotlib.pyplot as pl
import numpy as np
from scipy.optimize import curve_fit

import spectrum as sp


TIME_PERIOD = 13.158  # nanoseconds
ITERATIONS_NUMBER = 300
INDEX_LENGTH_AFTER_MAX = 10
INDEX_OF_GOOD_CURVE_START = 200


def strexp(t, ampl, tau, beta):
    """
    Stretched exponenti
    y  =  strexp(t, ampl, tau, beta)  =  ampl * np.exp(-t / tau) ** beta
    """
    return ampl * np.exp(-t / tau) ** beta


def strexp_loop(t, t_period, num, y0, ampl, tau, beta):
    """
    Looped stretched exponenti
    """
    s = y0
    for i in range(num):
        s += strexp(t + i * t_period, ampl, tau, beta)
    return s


def strexp_loop_func(t_period, num):
    return lambda t, y0, ampl, tau, beta: strexp_loop(t, t_period, num, y0,
                                                      ampl, tau, beta)


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


# Initial parameters = [y0, ampl, tau, beta]
tau = 15.0
beta = 0.3

for spec in data:
    # Initial parameters
    y0 = np.float(spec.y[0])
    ampl = np.float(np.max(spec.y))

    initial_params = [y0, ampl, tau, beta]

    maxpos = np.argmax(spec.y)
    t_shift = spec.x[maxpos]

    # The use of the curve maximum is useless for the exponent, so it's
    # inclusion is commented
    # xfit = np.concatenate( (spec.x[maxpos:maxpos + INDEX_LENGTH_AFTER_MAX],
    # spec.x[INDEX_OF_GOOD_CURVE_START:len(spec.x)]))
    # yfit = np.concatenate( (spec.y[maxpos:maxpos + INDEX_LENGTH_AFTER_MAX],
    # spec.y[INDEX_OF_GOOD_CURVE_START:len(spec.x)]))

    xfit = spec.x[INDEX_OF_GOOD_CURVE_START:len(spec.x)] - t_shift
    yfit = spec.y[INDEX_OF_GOOD_CURVE_START:len(spec.y)]

    # xfit = spec.x[maxpos:maxpos + INDEX_LENGTH_AFTER_MAX]
    # yfit = spec.y[maxpos:maxpos + INDEX_LENGTH_AFTER_MAX]

    # xfit = spec.x[maxpos:]
    # yfit = spec.y[maxpos:]

    print("Processing file", spec.headers['filepath'])
    try:
        params, _ = curve_fit(
            strexp_loop_func(TIME_PERIOD, ITERATIONS_NUMBER),
            xfit, yfit, initial_params)
    except RuntimeError:
        print("Couldn't find optimal parameters.")
        continue

    # Parameters are in order [y0, ampl, tau, beta]
    fmt = " [y0 = %d\tampl = %d\ttau = %.3f\tbeta = %.3f]"
    # print("  Initial params " + fmt % tuple(initial_params))
    print("  Fitted params  " + fmt % tuple(params))

    # Fitted sum of stretched exponents
    pl.semilogy(xfit, strexp_loop(xfit, TIME_PERIOD, ITERATIONS_NUMBER,
                                  *params))
    legend.append("Fitting %d + %d exp(-t/%.2f)^%.2f" % tuple(params))

    # Single stretched exponent
    pl.semilogy(xfit, params[0] + strexp(xfit, *params[1:]))
    legend.append("Single exp")

    # Initial params
    # pl.semilogy(xfit, initial_params[0] + strexp(xfit, *initial_params[1:]))
    # legend.append("Single exp with initial params")

    pl.semilogy(spec.x - t_shift, spec.y)
    legend.append(os.path.basename(spec.headers['filepath']))

pl.grid()
pl.legend(legend)
pl.show()
