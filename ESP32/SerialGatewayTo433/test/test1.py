import numpy as np
import math

source = [
    8758, 4737, 1415, 374, 700, 733, 339, 375, 717, 713, 346, 738, 343, 363, 707, 746, 342, 713, 354, 722, 367, 360,
    708, 730, 349, 724, 351, 712, 357, 719, 378, 702, 356, 719, 357, 708, 376, 348, 725, 714, 353, 371, 718, 716, 345,
    725, 370, 704, 360, 710, 357, 353, 734, 351, 711, 369, 717, 361, 707, 730, 334, 388, 702, 365, 712, 722, 349, 370,
    705, 727, 355, 355, 727, 718, 339, 374, 712, 718, 356, 356, 722, 713, 14383, 0
]

data = source[3:-2]
data.sort()


def detect_fill_interval(data):
    edges = []
    edge = None
    i = None
    hist, bin_edges = np.histogram(data, 20)
    for i, elem in enumerate(hist):
        if elem and not edge:
            edge = [math.floor(bin_edges[i]), 0]
            continue
        if not elem and edge:
            edge[1] = math.ceil(bin_edges[i])
            edges.append(edge)
            edge = None
    if edge and i:
        edge[1] = math.ceil(bin_edges[i])
        edges.append(edge)
    return edges


def detect_bit_time(data, intervals):
    _data = []
    # hist, bin_edges = np.histogram(data, 10, intervals[0])
    # hist, bin_edges = np.histogram(data, 10, intervals[0])

    for interval in intervals:
        _data.append([elem for elem in data if interval[0] <= elem <= interval[1]])

    hist, bin_edges = np.histogram(_data[0], 9)
    index = list(hist).index(max(hist))
    maximum1 = int(round(bin_edges[index] + bin_edges[index + 1] / 2))

    for i in range(len(intervals) - 1):
        for elem in _data[i + 1]:
            count = elem / bin_edges[index]
            count = int(round(count))
            value = round(elem / count)
            _data[0].extend([value for i in range(count)])
            pass
    # res = np.interp(_data[0])

    hist, bin_edges = np.histogram(_data[0], 20)
    index = list(hist).index(max(hist))
    maximum2 = int(round(bin_edges[index] + bin_edges[index + 1] / 2))
    return maximum2


def convert_to_bit(source, bit_time):
    bit_string = ''
    for elem in source:



pass

intervals = detect_fill_interval(data)
bit_time = detect_bit_time(data, intervals)
