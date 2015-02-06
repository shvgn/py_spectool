import numpy as np
from scipy import interpolate

__author__ = 'Evgenii Shevchenko'
__email__ = 'shevchenko@beam.ioffe.ru'
__date__ = '2015-02-04'


EVNM_CONST = 1239.84193
EVNM_BORDER = 100
SPLINE_ORDER = 5


def convert_nmev(x_array):
    """
    Convert array of nanometers to electron-volts and in reverse
    x -> 1239.84193 / x
    :param x_array:
    :return:
    """
    return np.array([EVNM_CONST / x for x in x_array])


def point_deriv(xary, yary, index):
    """
    """
    if len(xary) != len(yary):
        raise ValueError("X and Y must have the same length")

    length = len(xary)
    if index <= 0 or index >= length:
        raise ValueError("Index must be between zero and len-2")
    # Left derivative
    dl = (yary[index] - yary[index - 1]) / (xary[index] - xary[index - 1])
    # Rigth derivative
    dr = (yary[index + 1] - yary[index]) / (xary[index + 1] - xary[index])
    # Mean
    return 0.5 * (dl + dr)


def get_ref_data(file_or_number):
    import os
    # if not (os.path.exists(file_or_number) and os.path.isfile(file_or_number)):
    #     sys.exit("First argument: file not found or it's not a file")
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
            line = line.replace(",", ".")
            xy = line.split()
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
    return Spectrum(x, y, headers)


# TODO rename Spectrum class to XYData, because it has nothing to do with
# spectra, only manipulating two-column data
class Spectrum(object):
    __op_headers = {'__add__': 'added_to',
                    '__sub__': 'subtracted',
                    '__mul__': 'multiplied_by',
                    '__truediv__': 'divided_by'}

    def __init__(self, x, y, headers=None):
        self.x = np.array(x, dtype=float)  # Ensure numpy arrays of floats
        self.y = np.array(y, dtype=float)
        self.headers = headers

    def __add__(self, other):
        return self.__arithmetic(other, '__add__')

    def __sub__(self, other):
        return self.__arithmetic(other, '__sub__')

    def __mul__(self, other):
        return self.__arithmetic(other, '__mul__')

    def __truediv__(self, other):
        return self.__arithmetic(other, '__truediv__')

    def __arithmetic(self, other, method):
        """
        Arithmetic operation of the spectrum with a reference spectrum, the last being
        interpolated with 5-degree spline. See numpy.interpolation.interp1d for
        interpolation types.

        Supported operators are
        +   __add__     addition
        -   __sub__     subtraction
        *   __mul__     multiplication
        /   __truediv__ division
        """

        # Find out what's the operation
        # supported_operators = ("+", "-", "*", "/")

        # headers_op = ("added_to", "subtracted", "multiplied_by", "divided_by")
        supported_methods = ('__add__', '__sub__', '__mul__', '__truediv__')
        if method not in supported_methods:
            raise ValueError("Unsupported arithmetic operator")

        headers_new = self.headers

        # The second operand can be a number
        op_header = self.__op_headers[method]
        if isinstance(other, int) or isinstance(other, float):
            if op_header in self.headers:
                headers_new[op_header] += ", " + str(other)
            else:
                headers_new[op_header] = str(other)  # A number is here
            return Spectrum(self.x,
                            getattr(self.y, method)(other), headers_new)

        # Make the operation
        # If the second operand is not a number it must be a Spectrum instance
        if not other.__class__ == Spectrum:
            raise TypeError("Not Spectrum instance or a number")

        x_min = np.maximum(np.min(self.x), np.min(other.x))
        x_max = np.minimum(np.max(self.x), np.max(other.x))

        if x_max < x_min:
            raise ValueError("X ranges do not overlap")

        f = interpolate.interp1d(other.x, other.y, SPLINE_ORDER)

        x_new = np.array([], dtype=float)
        y_new = np.array([], dtype=float)
        for i in range(len(self.x)):
            if x_min <= self.x[i] <= x_max:
                x_new = np.append(x_new, self.x[i])
                y_new = np.append(
                    y_new, getattr(self.y[i], method)(f(self.x[i])))

        if 'filepath' in other.headers:
            headers_new[op_header] = other.headers['filepath']
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

    def y_shift(self):
        """
        Naively calculate horizontal shift of y from zero by estimating maximum of the
        points distribution, the y's being rounded and casted to int's.
        """
        counts = dict()
        # Populate statisctics
        for el in self.y:
            el = int(round(el))
            if counts.get(el, None) is None:
                counts[el] = 1
            else:
                counts[el] += 1

        # cnt_max = 0
        # for el in sorted(counts.keys()):
        #     counts[el]
        y_shift = max(counts, key=lambda x: counts[x])
        return y_shift

    def area(self):
        """
        Calculate area under the spectrum
        """
        s = 0
        for i in range(len(self.x) - 1):
            s += 0.5 * (self.y[i] + self.y[i + 1]) * \
                (self.x[i + 1] - self.x[i])
        return s
