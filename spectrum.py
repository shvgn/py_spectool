#!/usr/bin/env python3
# ~*~encoding: utf-8~*~

import sys
import os
import numpy as np
from scipy import interpolate

__author__ = 'Evgenii Shevchenko'
__email__ = 'shevchenko@beam.ioffe.ru'
__date__ = '2015-12-02'

EVNM_CONST = 1239.84193  # (1 eV) * (1 nm) = EVNM_CONST
EVNM_BORDER = 100  # eV < 100 <= nm
SPLINE_ORDER = 5  # Default order of spline interpolation


def convert_nmev(x_array):
    """
    Convert array of nanometers to electron-volts and in reverse
    x -> 1239.84193 / x
    """
    return np.array([EVNM_CONST / x for x in x_array])


def point_deriv(xary, yary, index):
    """
    point_deriv(xary, yary, index)

    The derivative of a chosen point (x(i), y(i)) at specified index 
    in passed arrays xary and yary
    """
    if len(xary) != len(yary):
        raise ValueError("X and Y must have the same length")

    length = len(xary)
    if index <= 0 or index >= length:
        raise ValueError("Index must be between zero and len-2")
    # Left derivative
    dl = (yary[index] - yary[index - 1]) / (xary[index] - xary[index - 1])
    # Right derivative
    dr = (yary[index + 1] - yary[index]) / (xary[index + 1] - xary[index])
    # Mean
    return 0.5 * (dl + dr)


def get_data_list(filelist, usagefmt='usage: {0} reffile datafile1 [datafile2 ...]',
                  minfiles=1, maxfiles=1024):
    """Returns a list of spectrum instances"""
    if len(filelist) < minfiles or len(filelist) > maxfiles:
        print(usagefmt.format(os.path.basename(filelist[0])))
        sys.exit(1)  # Maybe throwing an exception would be better here

    refdata = get_ref_data(filelist[1])
    datalist = []
    for fname in filelist[2:]:
        if not (os.path.exists(fname) and os.path.isfile(fname)):
            print("Warning! Cannot open file <" + fname + ">. Skipping.")
            continue
        datalist.append(spectrum_from_file(fname))

    ref_fname = str(refdata)
    if refdata.__class__ is Spectrum:
        ref_fname = os.path.basename(refdata.headers['filepath'])

    return ref_fname, refdata, datalist


def ary_deriv(xary, yary):
    """
    ary_deriv(xary, yary)

    Numeric derivative of y array over x array
    Return dy and dx with length-2 related to the input arrays
    """
    dx = np.array(xary[1:len(xary) - 1])
    dy = np.array([point_deriv(xary, yary, i)
                   for i in range(1, len(xary) - 1)])
    return dx, dy


def get_ref_data(file_or_number):
    """
    get_ref_data(file_or_number)

    Get reference data for a calculation via detecting whether the input is
    a number or a file path. Returns either float or Spectrum instance with
    the content of the file.
    """
    # if not (os.path.exists(file_or_number) and os.path.isfile(file_or_number)):
    # sys.exit("First argument: file not found or it's not a file")
    # refdata = spectrum_from_file(file_or_number)

    if os.path.exists(file_or_number) and os.path.isfile(file_or_number):
        refdata = spectrum_from_file(file_or_number)
    else:
        refdata = float(file_or_number)
    return refdata


def spectrum_from_file(filepath):
    """
    Returns Spectrum object with the data taken from passed file
    """
    x = np.array([])
    y = np.array([])
    headers = {'filepath': filepath}

    with open(filepath, 'r') as datafile:
        textdata = datafile.read().splitlines()

    for line in textdata:
        # Empty strings
        if line.strip() == '':
            continue
        try:
            xy = line.replace(",", ".")
            xy = xy.split()
            x = np.append(x, float(xy[0]))
            y = np.append(y, float(xy[1]))
        except ValueError:
            # If floats cannot be parsed the data is written to headers
            seps = [':', '=', None]
            for sep in seps:
                info = line.split(sep, 1)
                if len(info) == 2:
                    headers[info[0]] = info[1]
                    break
    headers = {'filepath': filepath}
    return Spectrum(x, y, headers)


# TODO rename Spectrum class to XYData, because it has nothing to do with
# spectra, and only manipulates two-column data
class Spectrum(object):
    '''
    Class for manipulation of two-column (X,Y) data with meta support
    '''
    __op_headers = {'__add__': 'added_to',
                    '__sub__': 'subtracted',
                    '__mul__': 'multiplied_by',
                    '__truediv__': 'divided_by',
                    '__pow__': 'exponentiated_by' }

    def __init__(self, x, y, headers=None):
        if len(x) != len(y):
            raise ValueError("X and Y must be of the same length")
        if len(x) == 0:
            raise ValueError("Spectrum data must be non-zero, received zero length")
        # Ensure X is sorted in ascending order
        self.x, self.y = zip(*sorted(list(zip(x, y))))
        self.x = np.array(self.x, dtype=float)
        self.y = np.array(self.y, dtype=float)
        self.headers = headers

    def __add__(self, other):
        return self.__arithmetic(other, '__add__')

    def __sub__(self, other):
        return self.__arithmetic(other, '__sub__')

    def __mul__(self, other):
        return self.__arithmetic(other, '__mul__')

    def __truediv__(self, other):
        return self.__arithmetic(other, '__truediv__')

    def __pow__(self, other):
        return self.__arithmetic(other, '__pow__')

    def __arithmetic(self, other, method, verbose=True, spline_order=SPLINE_ORDER):
        """
        Arithmetic operation of the spectrum with a reference spectrum, 
        the last being interpolated with 5-degree spline. 
        See numpy.interpolation.interp1d for interpolation types.

        Supported operators are
        +   __add__      addition
        -   __sub__      subtraction
        *   __mul__      multiplication
        /   __truediv__  division
        **  __pow__      exponentiation
        """

        # Find out what's the operation
        supported_methods = self.__op_headers.keys()
        if method not in supported_methods:
            raise ValueError("Unsupported arithmetic operator")

        opstring = "WTF we are doing with"
        pron = "and"
        if method == '__add__':
            # Adding file to argument
            opstring = "Adding"
            pron = "to"
        elif method == '__sub__':
            # Subtracting argument from file
            # From file subtracting argument
            opstring = "From"
            pron = "subtracting"
        elif method == '__mul__':
            # Multiplying file by argument 
            opstring = "Multiplying"
            pron = "by"
        elif method == '__truediv__':
            # Dividing file by argument 
            opstring = "Dividing"
            pron = "by"
        elif method == '__pow__':
            # Raising file to the argument 
            opstring = "Raising"
            pron = "to the"

        opfmt = opstring + " %s " + pron + " %s"

        headers_new = self.headers

        # The second argument can be a number
        op_header = self.__op_headers[method]
        if isinstance(other, int) or isinstance(other, float):
            if op_header in self.headers:
                headers_new[op_header] += ", " + str(other)
            else:
                headers_new[op_header] = str(other)  # A number is here
                if verbose:
                    print(opfmt % (self.headers['filepath'], str(other)))
            return Spectrum(self.x,
                            getattr(self.y, method)(other), headers_new)

        # Make the operation
        # If the second operand is not a number it must be a Spectrum instance
        if not other.__class__ == Spectrum:
            raise TypeError("Not Spectrum instance or a number")

        x_min = np.maximum(np.min(self.x), np.min(other.x))  # Min is max of mins
        x_max = np.minimum(np.max(self.x), np.max(other.x))  # Max is min of maxes
        oth_shift = 0  # Shift of the other spectrum X index if X's coincide.
        # TODO calculate the oth_shift

        if x_max < x_min:
            raise ValueError("X ranges do not overlap")

        interpolator_used = False
        f = None
        # f = interpolate.interp1d(other.x, other.y, SPLINE_ORDER)
        x_new = np.array([], dtype=float)
        y_new = np.array([], dtype=float)
        for i in range(len(self.x)):
            if x_min <= self.x[i] <= x_max:  # If we are in the range
                x_new = np.append(x_new, self.x[i])
                if self.x[i] != other.x[i + oth_shift]:
                    if interpolator_used is False:
                        f = interpolate.interp1d(other.x, other.y, spline_order)
                        interpolator_used = True
                    y_new = np.append(
                        y_new, getattr(self.y[i], method)(f(self.x[i])))
                else:
                    y_new = np.append(y_new, getattr(self.y[i], method)(other.y[i + oth_shift]))

        if 'filepath' in other.headers:
            headers_new[op_header] = other.headers['filepath']
        if verbose:
            print(opfmt % (self.headers['filepath'], other.headers['filepath']))
        return Spectrum(x_new, y_new, headers_new)

    def __str__(self):
        """
        Text data representation
        """
        max_header_len = np.max([len(s) for s in self.headers.keys()])
        header_txt = '\n'.join(k.rjust(max_header_len) + ":\t" + v
                               for (k, v) in self.headers.items())
        data_txt = '\n'.join("%f\t%f" % (k, v) for (k, v)
                             in zip(self.x, self.y))
        return header_txt + "\n\n" + data_txt

    def __len__(self):
        """
        Number of the data points (x,y), Technically it is length of X and Y.
        If len(self.x) and len(self.y) is not he same ValeError raises.
        """
        if len(self.x) == len(self.y):
            return len(self.x)
        raise ValueError("X and Y are not of the same length")

    def y_shift(self):
        """
        Naively calculate horizontal shift of y from zero by estimating maximum
        of the points distribution, the y's being rounded and casted to
        integers. This method might be useful for estimation of a spectrum
        noise level in case its amplitude is much higher than 1 so the rounding
        will not affect the accuracy dramatically. The noise (dark Y) signal is
        assumed to be constant and to take the majority of the signal length (X)
        """
        counts = dict()
        # Populate statistics
        for el in self.y:
            el = int(round(el))
            if counts.get(el, None) is None:
                counts[el] = 1
            else:
                counts[el] += 1

        # cnt_max = 0
        # for el in sorted(counts.keys()):
        # counts[el]
        y_shift = max(counts, key=lambda x: counts[x])
        return y_shift

    def area(self):
        """
        Calculate area under the Y curve
        """
        s = 0
        for i in range(len(self.x) - 1):
            s += 0.5 * (self.y[i] + self.y[i + 1]) * (self.x[i + 1] - self.x[i])
        return s

    def xfilter(self, xl=None, xr=None):
        """
        Choose X interval from xl to xr
        """
        lpos = 0
        rpos = len(self.x) - 1
        xmin = self.x[0]
        xmax = self.x[rpos]
        need_new = False
        if xl is not None and xl > xmin:
            lpos = np.argmin(np.abs(self.x - xl))
            need_new = True
        if xr is not None and xr < xmax:
            rpos = np.argmin(np.abs(self.x - xr))
            need_new = True
        if need_new:
            return Spectrum(self.x[lpos:rpos], self.y[lpos:rpos], self.headers)
        return self

    def min(self, xleft=None, xright=None):
        """ 
        (x, y, idx) = spectrum.min(xleft, xright)
        Returns minimum y, its x and its index in the range between [xleft, xright], both
        xleft and xright default to None which means the whole spectrum X range
        """
        need_new = True
        posshift = 0
        if (xleft is None) and (xright is None):
            need_new = False
        if xleft is None:
            xleft = self.x[0]
        if xright is None:
            xright = self.x[len(self.x) - 1]
        spcut = self
        if need_new:
            spcut = self.xfilter(xleft, xright)
            if xleft != self.x[0]:
                posshift = np.argmin(np.abs(self.x - xleft))
        minpos_local = np.argmin(spcut.y)
        minpos = minpos_local + posshift
        return spcut.x[minpos_local], spcut.y[minpos_local], minpos


if __name__ == '__main__':
    print("this is Spectrum class file, not a python script")
