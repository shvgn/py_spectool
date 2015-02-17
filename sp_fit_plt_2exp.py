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
from scipy.odr import odrpack as odr

import spectrum as sp


CONST_BOLZMANN = 8.6173324e-5  # eV / K


def coreexp(t0, p, t):
    """
    Exponential thermal PL quenching
    p = [c, e]
    I = coreexp(t0, p, t) =
      =  (1 + c * np.exp(-e / (CONST_BOLZMANN * (t - t0))) ) ** -1
    """
    a = p[0]
    c = p[1]
    e = p[2]
    return a * (1 + c * np.exp(-e / (CONST_BOLZMANN * (t - t0)))) ** -1


def coreexp2(t0, p, t):
    """
    Double exponential thermal PL quenching
    p = [c1, c2, e1, e2]
    I = corefunc(t0, p, t) =
      =  (1 + c1 * np.exp(-e1 / (CONST_BOLZMANN * (t - t0))) + c2 * np.exp(-e2 / (CONST_BOLZMANN * (t - t0)))) ** -1
    """
    c1 = p[0]
    c2 = p[1]
    e1 = p[2]
    e2 = p[3]
    return (1 + c1 * np.exp(-e1 / (CONST_BOLZMANN * (t - t0))) + c2 * np.exp(-e2 / (CONST_BOLZMANN * (t - t0)))) ** -1


def fitfunc(t0, func):
    """
    Single or double exponent thermal PL quenching closure with defined t0
    I = fitfunc(t0, corefunc) -> corefunc(p, t) @ t0
    """
    return lambda p, t: func(t0, p, t)


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

# initial_params = [100., 5., 0.05, 0.01]
initial_params = [1.1, 80., 0.092]
for spec in data:

    maxidx = np.argmax(spec.y)
    spec = spec / np.max(spec.y)  # Normalize by Y maximum
    if maxidx < 15:
        maxidx = 15
        spec = spec / spec.y[maxidx]

    # t0 = spec.x[maxidx]
    t0 = 0.0

    xdata = spec.x[maxidx:len(spec)]
    ydata = spec.x[maxidx:len(spec)]
    func = coreexp
    model = odr.Model(fitfunc(t0, func))
    data = odr.Data(xdata, ydata)

    fitting = odr.ODR(data, model, beta0=initial_params)
    fitting.set_job(fit_type=2)  # 2 corresponds to least squares
    fitres = fitting.run()

    fitres.pprint()
    # print(fitres.beta)
    # print(fitres.cov_beta)
    # print(fitres.sd_beta)


    # try:
    # params, conv = curve_fit(fitfunc(t0), xdata, ydata, p0=initial_params)
    # print(conv)
    # except RuntimeError:
    # # print("Couldn't find optimal parameters.")
    # print(spec.headers['filepath'], "\t-\t-\t-\t-")
    # continue
    #
    # # Parameters are in order [c1, c2, e1, e2]
    # fmt = "\t%f\t%f\t%f\t%f"
    # print(spec.headers['filepath'], fmt % tuple(params))
    # # print(spec.headers['filepath'], params)
    #
    # # Fitted sum of stretched exponents
    # pl.plot(1 / xdata, corefunc(xdata, t0, *params))
    # # pl.semilogy(1 / xfit, fitfun(xfit, t0, *params))
    # legend.append("Fitting [c1=%.2f, c2=%.2f, e1=%.2f, e2=%.2f]" % tuple(params))
    #

    # Fitted params
    pl.plot(xdata, func(t0, fitres.beta, xdata))
    # pl.semilogy(1 / xfit, fitfun(xfit, t0, *initial_params))
    legend.append("Fitted " + str(tuple(fitres.beta)))
    # legend.append("Fitted [c1=%.2f, c2=%.2f, e1=%.2f, e2=%.2f]" % tuple(fitres.beta))

    # Initial params
    pl.plot(xdata, func(t0, initial_params, xdata))
    # pl.semilogy(1 / xfit, fitfun(xfit, t0, *initial_params))
    legend.append("Initial " + str(tuple(initial_params)))
    # legend.append("Initial [c1=%.2f, c2=%.2f, e1=%.2f, e2=%.2f]" % tuple(initial_params))

    # Original data
    pl.plot(spec.x, spec.y, 'o')
    # pl.semilogy(1 / spec.x, spec.y)
    legend.append(os.path.basename(spec.headers['filepath']))

pl.grid()
pl.legend(legend)
pl.show()
