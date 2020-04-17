import numpy as np
import math
from .Dooya import Dooya


class BinarySignal:
    def __init__(self, **kwargs):
        self.x_0 = 20
        self.y_0 = 20
        self.x_max = 0
        self.signal_height = 20
        self.y_max = self.signal_height + self.y_0 * 2
        self.data = kwargs.get('data', None)
        self.raw = None
        self.bit_time = None
        self.scale = 100
        self.svg = None
        self.len_data = 0
        pass

    def prepare_data(self, source):
        # if source[0:6] != 'L10000':
        #     raise KeyError('Bad data')
        self.x_max = 0
        _data = source.split(';')
        data = []
        i = 0
        full_time = 0
        for elem in _data:
            try:
                time = int(elem[1:])
                full_time += time
                data.append((1 if elem[0:1] == 'H' else 0, time))
            except ValueError:  # конец строки
                break

        return data

    def decode(self, signal):
        self.raw = signal
        try:
            data = self.prepare_data(signal)
            if len(data) < 7:
                return
            _data = [x[1] for x in data]
            intervals = self.detect_fill_interval(_data)
            self.bit_time = self.detect_bit_time(_data[3:-1], intervals)
            self.data = int(self.convert_to_bit(data[1:-1], self.bit_time) + '0', base=2)
            return self.data
        except KeyError:
            pass
        except Exception as e:
            raise KeyError(e) from e

    def detect(self):
        result = []
        devices = [
            Dooya
        ]
        # _data = '{0:x}'.format(self.data)
        for device in devices:
            _res = device().detect(self.data)
            if _res:
                result.append(_res)
        return result

    @classmethod
    def detect_fill_interval(cls, data):
        _data = data
        while True:
            hist, bin_edges = np.histogram(_data, 20)
            edges = cls.remove_zero_interval(hist, bin_edges)
            if len(edges) == 1:
                _data = cls.split_into_intervals(data, edges)
            else:
                return edges

    @staticmethod
    def remove_zero_interval(hist, bin_edges):
        # склеиваем не нулевые соседние
        edges = []
        min_signal_count = 3
        edge = None
        size = len(hist)
        for i, elem in enumerate(hist):
            if elem > min_signal_count and not edge:  # новый интервал
                edge = [math.floor(bin_edges[i]), 0, elem]
            elif elem > min_signal_count and edge:  # продолжается существущий инетрвал
                edge[2] += elem
            elif not elem > min_signal_count and edge:  # закончился интервал
                edge[1] = math.ceil(bin_edges[i])
                edge[2] += elem
                edges.append(edge)
                edge = None
            if i == size - 1 and edge:
                edge[1] = math.ceil(bin_edges[i])
                edge[2] += elem
        return edges

    @staticmethod
    def split_into_intervals(data, intervals):
        _data = []
        for interval in intervals:
            _data.append([elem for elem in data if interval[0] <= elem <= interval[1]])
        return _data

    @classmethod
    def detect_bit_time(cls, data, intervals):
        _data = cls.split_into_intervals(data, intervals)

        hist, bin_edges = np.histogram(_data[0], 9)
        index = list(hist).index(max(hist))
        maximum = int(round(bin_edges[index] + bin_edges[index + 1]) / 2)

        hist1, bin_edges1 = np.histogram(_data[1], 9)
        index = list(hist1).index(max(hist1))
        maximum1 = int(round(bin_edges1[index] + bin_edges1[index + 1]) / 2)

        for i in range(len(intervals) - 1):
            for elem in _data[i + 1]:
                count = elem / bin_edges[index]
                count = int(round(count))
                value = round(elem / count)
                _data[0].extend([value for i in range(count)])
                pass
        # res = np.interp(_data[0])

        hist2, bin_edges2 = np.histogram(_data[0], 20)
        index = list(hist2).index(max(hist2))
        maximum2 = int(round(bin_edges2[index] + bin_edges2[index + 1]) / 2)
        return maximum2

    @staticmethod
    def convert_to_bit(source, bit_time):
        bit_string = ''
        for elem in source:
            count1 = elem[1] / bit_time
            count = int(round(count1))
            value = str(elem[0])
            bit_string += value.rjust(count, value)
        return bit_string
