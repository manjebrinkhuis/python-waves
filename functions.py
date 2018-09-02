from math import floor, e
import sys

def linear(xprop, ys):
    """ Linear interpolation """
    max_index = len(ys)-1
    x = max_index * xprop
    x0 = int(floor(x))
    x1 = int(x0+1)
    if x1 > max_index:
        return ys[-1]
    else:
        y0 = ys[x0]
        y1 = ys[x1]
        return y0 + (y1-y0)*((x-x0)/(x1-x0))


def nearest(xprop, ys):
    """ Nearest neighbor """
    index = int(floor(xprop * (len(ys))))
    return ys[index]


def rescale(ys, ymin=0, ymax=1):
    """ Return rescaling parameters given a list of values,
    and a new minimum and maximum. """

    bounds = min(ys), max(ys)
    ys_range = bounds[1] - bounds[0]
    new_range = ymax - ymin

    ys_mid = sum(bounds)*.5
    new_mid = sum([ymax, ymin])*.5
    scale = float(new_range) / ys_range

    return scale, ys_mid, new_mid


def euclidean_rhythm(steps=16, pulses=4, shift=0, length=1, onset=False):
    """euclidean rhythm

    Returns a list with a given number of pulses
    spaced as equally as possible over a given number
    of steps. Based on the paper 'The Euclidean Algorithm
    Generates Traditional Musical Rhythms' by Godfried
    Toussaint (2005). Optionally, it gives the note onsets
    using a bar with duration "length". Rewritten from bjorklund
    function.

    """

    # Create the pattern with pulses (ones) and zeros
    pattern = [[1] for i in range(pulses)]
    suffix = [[0] for i in range(steps - pulses)]

    # Iterate
    while len(suffix) > 1:
        for i, sf in enumerate(suffix):
            if pattern:
                pattern[i % len(pattern)] += sf
            else:
                pattern.append(sf)

        # Reshift
        lsuf = len(suffix)
        lpat = len(pattern)
        suffix = pattern[(lsuf % lpat):]
        pattern = pattern[:(lsuf % lpat)]

    # output flattened list, and shift
    pattern = pattern + suffix
    pattern = [bool(val) for L in pattern for val in L]
    pattern = pattern[-shift:] + pattern[:-shift]

    if onset:
        onsets = [i*(1.0/steps) for i in range(steps) if pattern[i]]
        onsets = [on*length for on in onsets]
        output = (pattern, onsets)
    else:
        output = pattern

    return output


def cumsum(arr):
    """ Cumulative sum. Start at zero. Exclude arr[-1]. """
    return [sum(arr[:i]) for i in range(len(arr))]


def roll(arr, step):
    """ Roll array, by "step". """
    return arr[step:] + arr[:step]


def diff(arr1, arr2):
    """ Return difference between two arrays. """
    return [i - j for i, j in zip(arr1, arr2)]


def diff_single(arr, val):
    """ Return difference between array and scalar. """
    return [i - val for i in arr]


def add(*args):
    """ Return sum of any number of arrays. """
    return [sum(vals) for vals in zip(*args)]


def add_single(arr, val):
    """ Return sum of array and scalar. """
    return [i + val for i in arr]


def abs_array(arr):
    """ Return absolute array. """
    return [abs(i) for i in arr]


def equal(*args):
    """ Return boolean array for equal values in any number of arrays. """
    return [vals[1:] == vals[:-1] for vals in zip(*args)]


def mul_single(arr, val):
    """ Multiply array with scalar. """
    return [val * i for i in arr]


def floor_div(arr, val):
    """ Floor division of array by value. """
    return [i // val for i in arr]


def modulo(arr, val):
    """ Modulo division of array by value. """
    return [i % val for i in arr]


def argsort(arr):
    """ Return indices of ordered values in list. """
    out = []
    for i in sorted(set(arr)):
        check_from = 0
        for j in range(arr.count(i)):
            index = arr.index(i, check_from)
            out.append(index)
            check_from = index + 1
    return out


def linspace(start, end, num=50):
    """ Return equally spaced array from "start" to "end" with "num" vals. """
    return [start+i*((end-start)/float(num-1)) for i in range(num)]


def leading_zeros(val, n):
    """ Return string with "n" leading zeros to integer. """
    return (n - len(str(val))) * '0' + str(val)


def secs2time(secs):
    """ Return string with hours, minutes, seconds and subseconds """

    secs = float(secs)

    # Hours
    hours = int(secs // 3600)
    remaining = secs % 3600

    # Minutes
    minutes = int(remaining // 60)
    remaining = remaining % 60

    # Seconds
    seconds = int(floor(remaining))
    remaining = remaining - floor(remaining)

    # Subseconds
    subseconds = int(round(remaining, 3) * 1000)

    # Combine
    the_time = [leading_zeros(hours, 2),
                leading_zeros(minutes, 2),
                leading_zeros(seconds, 2),
                leading_zeros(subseconds, 3)]

    return ':'.join(the_time)


def dashed_string(string, dashes=20, dash='-'):
    """ Pretty dashed string. """
    if string:
        sides = ((dashes - len(string)) / 2) - 1
        out = dash*sides + ' ' + string + ' ' + dash*sides
        out += dash*(dashes-len(out))
    else:
        out = dash*dashes
    return out


def print_note(the_time, name, velocity, msg, channel, col_width=14):
    """ Print pretty notes. """
    line = [the_time]
    cols = ['']*int(channel) + [name + ' (' + velocity +') ' + msg]
    line += [dashed_string(col, col_width) for col in cols]
    sys.stdout.write(' | '.join(line) + '\n')


def flatten_list(lol, max_deg=1):
    """ recursively flatten list into single depth list. """
    flat_list = []
    for item in lol:
        if hasattr(item, '__iter__') and max_deg > 0:
            flat_list += flatten_list(item, max_deg-1)
        else:
            flat_list.append(item)
    return flat_list
