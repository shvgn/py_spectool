#!/usr/bin/env python3
# ~*~encoding: utf-8~*~

import os
import sys

import numpy as np
from scipy import interpolate


EVNM_CONST = 1239.84193  # (1 eV) * (1 nm) = EVNM_CONST
EVNM_BORDER = 100  # eV < 100 <= nm
SPLINE_ORDER = 5  # Default order of spline interpolation


def convert_nmev(x_array):
    """
    Convert array of nanometers to electron-volts and in reverse
    x -> 1239.84193 / x
    """
    return np.array([EVNM_CONST / x for x in x_array])


def check_and_exit(data):
    """Check whether the argument is Spectrum instance and exit otherwise"""
    if not data.__class__ is Spectrum:
        print("Not XY data: {0}".format(data))
        sys.exit(1)


def get_ref_data(file_or_number):
    """
    Get reference data for a calculation via detecting whether the input is
    a number or a file path. Returns either float or Spectrum instance with
    the content of the file.
    """
    if os.path.exists(file_or_number) and os.path.isfile(file_or_number):
        refdata = spectrum_from_file(file_or_number)
    else:
        refdata = float(file_or_number)
    return refdata


def get_data_list(filelist, usagefmt='usage: {0} reffile datafile1 [datafile2 ...]',
                  minfiles=1, maxfiles=1024):
    """Returns a list of spectrum instances"""
    if not minfiles < len(filelist) < maxfiles:
        print(usagefmt.format(os.path.basename(filelist[0])))
        sys.exit(1)  # Maybe throwing an exception would be better here

    refdata = get_ref_data(filelist[1])
    datalist = []
    for fname in filelist[2:]:
        if not (os.path.exists(fname) and os.path.isfile(fname)):
            print("Cannot open file <" + fname + ">. Skipping.")
            continue
        datalist.append(spectrum_from_file(fname))

    ref_fname = str(refdata)
    if refdata.__class__ is Spectrum:
        ref_fname = os.path.basename(refdata.headers['filepath'])

    return ref_fname, refdata, datalist


def point_deriv(x, y, i):
    """
    The derivative in chosen point (x(i), y(i)) at specified i
    in passed arrays x and y
    """
    if len(x) != len(y):
        raise ValueError("X and Y must have the same length")
    if i <= 0 or i >= len(x):
        raise ValueError("Index must be between zero and len-2")
    # Left derivative
    dl = (y[i] - y[i - 1]) / (x[i] - x[i - 1])
    # Right derivative
    dr = (y[i + 1] - y[i]) / (x[i + 1] - x[i])
    # Mean
    return 0.5 * (dl + dr)


def ary_deriv(x, y):
    """
    Numeric derivative of y array over x array
    Return dy and dx with length-2 related to the input arrays
    """
    dx = np.array( x[ 1 : len(x)-1 ])
    dy = np.array([ point_deriv(x, y, i) for i in range( 1, len(x)-1 )])
    return dx, dy


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
            x = np.append(x, [float(xy[0])])  # FIXME Expecxted Union[ndarray, iterable], got float
            y = np.append(y, [float(xy[1])])  # FIXME Expecxted Union[ndarray, iterable], got float
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
    """
    Class for manipulation of two-column (X,Y) data with meta support
    """
    __op_headers = {'__add__':     'added_to',
                    '__sub__':     'subtracted',
                    '__mul__':     'multiplied_by',
                    '__truediv__': 'divided_by',
                    '__pow__':     'exponentiated_by'}

    def __init__(self, x, y, headers=None):
        if len(x) != len(y):
            raise ValueError("X and Y must be of the same length")
        if len(x) == 0:
            raise ValueError("Spectrum data must be non-zero")
        # Ensure X is sorted in ascending order
        self.x, self.y = zip(*sorted(list(zip(x, y))))
        self.x = np.array(self.x, dtype=float)
        self.y = np.array(self.y, dtype=float)
        if headers.__class__ is not dict and headers is not None:
            raise ValueError("headers must be a dict")
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

    def __arithmetic(self, other, method, verbose=False, spline_order=SPLINE_ORDER):
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
            pron = "to"

        opfmt = opstring + " %s " + pron + " %s"

        headers_new = self.headers.copy()

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

        x_min, x_max, shift, length = self.overlap(other)
        shift1, shift2 = 0, 0
        if shift > 0:
            shift1 = shift
        else:
            shift2 = -shift

        x_new = np.zeros(length)
        y_new = np.zeros(length)
        using_interpolation = False
        f = None

        for i in range(length):
            # print(i)
            x_new[i] = self.x[i + shift1]
            # print("len(x_new) = {0}".format(len(x_new)))
            if x_new[i] == other.x[i + shift2]:
                y_new[i] = getattr(self.y[i + shift1], method)( other.y[i + shift2] )
                continue
            if using_interpolation is False:
                f = interpolate.interp1d(other.x, other.y, spline_order)
                using_interpolation = True
            y_new[i] = getattr(self.y[i + shift1], method)( f( x_new[i] ))

        if 'filepath' in other.headers:
            headers_new[op_header] = other.headers['filepath']
        if verbose:
            print(opfmt % (self.headers['filepath'], other.headers['filepath']))

        return Spectrum(x_new, y_new, headers_new)

    def overlap(self, other):
        """
        Returns overlap properties: minimum, maximum, index shift and overlap
        length (x_min, x_max, shift, length) if spectra overlap, otherwise
        raises ValueError.
        """
        if other.__class__ is not Spectrum:
            raise ValueError("Need a Spectrum in merge")
        min1, max1 = self.x[0], self.x[-1]
        min2, max2 = other.x[0], other.x[-1]
        x_min = np.maximum(min1, min2)  # Min is max of mins
        x_max = np.minimum(max1, max2)  # Max is min of maxes
        if x_max < x_min:
            raise ValueError("X ranges do not overlap")
        i1 = np.where(self.x >= x_min)[0][0]
        i2 = np.where(other.x >= x_min)[0][0]
        shift = i1 - i2
        length = 0
        if shift > 0:
            length = np.minimum(len(self) - shift, len(other))
        else:
            length = np.minimum(len(other) + shift, len(self))
        return x_min, x_max, shift, length

    def merge(self, other):
        """
        Merge this spectrum with the other one.
        The overlap is linearly weighted.
        """
        xmin, xmax, shift, length = self.overlap(other)
        if shift == 0:
            return
        shift1, shift2 = 0, 0
        if shift > 0:
            shift1 = shift
        else:
            shift2 = -shift

        for i in range(length):
            c2 = (i + 1) / (length + 1)
            c1 = 1 - c2
            self.y[shift1 + i] = c1 * self.y[shift1 + i] + c2 * other.y[shift2 + i]

        if shift > 0:
            self.x = np.append(self.x, other.x[shift2 + length:])
            self.y = np.append(self.y, other.y[shift2 + length:])
            # TODO headers stuff
        else:
            temp_x = other.x.copy()
            temp_y = other.y.copy()
            temp_x = np.append(temp_x, self.x[:length])
            temp_y = np.append(temp_y, self.y[:length])
            self.x = temp_x
            self.y = temp_y
            # TODO headers stuff

    def __str__(self):
        """
        String representation
        """
        max_header_len = np.max([len(s) for s in self.headers.keys()])
        header_txt = '\n'.join(k.rjust(max_header_len) + ":\t" + v
                               for (k, v) in self.headers.items())
        data_txt = '\n'.join("%f\t%f" % (k, v) for (k, v)
                             in zip(self.x, self.y))
        return header_txt + "\n\n" + data_txt

    def __len__(self):
        """
        Number of the data points (x,y)

        Technically it is length of X and Y.  If len(self.x) and len(self.y)
        are do not coincise ValeError raises.
        """
        if len(self.x) == len(self.y):
            return len(self.x)
        raise ValueError("X and Y are not of the same length")

    def y_shift(self):
        """
        Returns noise level.

        Naively calculate horizontal shift of y from zero by estimating maximum
        of the points distribution, the Y's being rounded and casted to
        np.log10( abs(Ymax) / abs(Ymin) ). This method might be useful for
        estimation of a spectrum noise level. The noise (dark Y) signal is
        assumed to be constant and to take the majority of the signal length.
        """
        counts = dict()
        y_min = np.min(np.abs(y))
        y_max = np.max(np.abs(y))
        round_order = np.int( np.ceil( np.log10( y_max / y_min )))
        # Populate statistics
        for el in self.y:
            el = int(round(el, round_order))
            if counts.get(el, None) is None:
                counts[el] = 1
            else:
                counts[el] += 1
        # TODO better take left shoulder of the distribution peak
        y_shift = max(counts, key=lambda x: counts[x])
        return y_shift

    def area(self):
        """
        Area under the Y curve
        """
        s = 0
        for i in range(len(self.x) - 1):
            s += 0.5 * (self.y[i] + self.y[i + 1]) * (self.x[i + 1] - self.x[i])
        return s

    def xfilter(self, xl=None, xr=None):
        """
        Cut X interval from xl to xr
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

    def min(self, xl=None, xr=None):
        """
        Returns x, y and the index of minimum Y in the range [xl, xr].
        Both xl and xr default to None which means the whole spectrum X range.

        min(self, xl=None, xr=None)
        """
        need_new = True
        posshift = 0
        if xl is None and xr is None:
            need_new = False
        if xl is None:
            xl = self.x[0]
        if xr is None:
            xr = self.x[len(self.x) - 1]
        spcut = self
        if need_new:
            spcut = self.xfilter(xl, xr)
            if xl != self.x[0]:
                shift = np.argmin( np.abs(self.x - xl) )
        min_pos_local = np.argmin( spcut.y )
        min_pos = min_pos_local + shift
        return spcut.x[min_pos_local], spcut.y[min_pos_local], min_pos


if __name__ == '__main__':
    print("this is Spectrum class file, not a python script")
