import numpy as np
import math


# from .Dooya import Dooya


class BinarySignal:
    def __init__(self, **kwargs):
        # self.x_0 = 20
        # self.y_0 = 20
        # self.x_max = 0
        # self.signal_height = 20
        # self.y_max = self.signal_height + self.y_0 * 2
        # self.scale = 100
        # self.svg = None
        # self.len_data = 0

        self.data = kwargs.get('data', None)
        self.raw = kwargs.get('raw', None)
        self.di = kwargs.get('di', None)
        self.n = kwargs.get('n', None)
        self.cmd = kwargs.get('cmd', None)
        self.props = dict()
        self.bit_length = None
        self.preamble_h = 0
        self.bits_count = 0
        self.preamble_l = 0
        self.matched = 0
        self.props_count = 0
        self.driver = None
        pass

    def decode(self, signal):
        if signal[0:6] != 'L8000;':
            raise KeyError('Bad signal: not prefix L8000;')
        self.raw = signal
        data = self._prepare_data(signal[6:])
        if len(data) < 7:
            raise KeyError('Bad signal: short')
        _data = [x[1] for x in data]
        self.preamble_h = _data[0]
        self.preamble_l = _data[1]
        intervals = self.detect_fill_interval(_data[2:])  # без преамбулы
        if not intervals:
            raise KeyError('Bad signal: not detect intervals')
        self.bit_length = self._detect_bit_length(_data[2:], intervals)
        bits = self.convert_to_bit(data[2:], self.bit_length) + '0'
        # self.bits_count = len(bits)
        self.data = int(bits, base=2)
        return self.data

    # def to_dict(self):
    #     result = dict(
    #         data=None,
    #         raw=None,
    #         device_uid=self.device_uid,
    #         device_title=self.device_title,
    #         device_command=self.device_command,
    #         device_detail=self.detail,
    #     )
    #     if self.device_uid and self.device_title and self.device_command:
    #         return result
    #     else:
    #         result['data'] = self.data
    #         result['raw'] = self.raw
    #         return result

    def detect_signal(self, signature):
        signal = BinarySignal()
        _data = '{0:x}'.format(self.data)
        for name in signature:
            prop = signature[name]
            if prop.get('position'):
                position = prop['position']
                value = _data[position[0]:position[1]]
                if 'items' in prop:
                    signal.props_count += 1
                    found = False
                    for item in prop['items']:
                        if value in prop['items'][item]:
                            signal.matched += 1
                            if 'name' in prop:
                                signal.props[name] = item
                            found = True
                            break
                    if not found and prop.get('unknown'):
                        signal.props_count -= 1
                        signal.props[name] = value
                else:
                    signal.props[name] = value
            elif prop.get('min') and prop.get('max'):
                if hasattr(self, name):
                    signal.props_count += 1
                    value = getattr(self, name)
                    if prop['min'] <= value <= prop['max']:
                        signal.matched += 1
                        signal.props[name] = value
            else:
                signal.props[name] = prop.get('default')
        signal.matched = int(round(signal.matched / signal.props_count * 100))
        if signal.matched < 50:
            return None
        signal.cmd = signal.props.get('cmd')
        signal.di = signal.props.get('di')
        signal.driver = signal.props.get('driver')
        signal.n = signal.props.get('n_tmpl', 'Unknown').format(**signal.props)
        return signal

    def encode_to_raw(self):
        # data = int('{preamble_h:x}{preamble_l:x}{data:x}'.format(data=self.data, **self.props), 16)
        data = '{0:b}'.format(self.data)
        size_bit = self.props['bit_length']
        signal = ''
        if data[0] != '1':
            raise Exception('Bad encoded signal: first char not 1')
        h = True
        size = 0
        size_data = len(data)
        for i, elem in enumerate(data):
            if int(elem) != h:
                signal += '{0}{1};'.format('H' if h else 'L', size)
                size = size_bit
                h = not h
            else:
                size += size_bit
            if i == size_data - 1:
                if h:
                    raise Exception('!!!')
        signal = 'L8000;H{0};L{1};{2}L2000;'.format(self.props['preamble_h'], self.props['preamble_l'], signal)
        return signal

    def encode(self, signature):
        self.set_default_props(signature)
        self.props['cmd'] = signature['cmd']['items'][self.cmd][0]
        self.data = int(self.props['data_tmpl'].format(**self.props), 16)
        self.raw = self.encode_to_raw()
        return self.raw

    @staticmethod
    def load_signature_from_file(path):
        import os
        import json
        try:
            with open(os.path.normpath(path), 'r', encoding='utf-8') as file:
                raw_data = json.load(file)
            signature = dict()
            if raw_data:
                for elem in raw_data:
                    signature[elem['name']] = elem
            return signature
        except Exception as e:
            raise Exception('Error load signature {0}: {1}'.format(config_path, e))


    @staticmethod
    def _prepare_data(source):
        # self.x_max = 0
        _data = source.split(';')
        data = []
        full_time = 0
        for elem in _data[0:-1]:  # последний элемент всегда пустой
            level = elem[0:1]
            if level == 'H':
                level = 1
            elif level == 'L':
                level = 0
            else:
                raise KeyError('Bad char in signal ({0})'.format(level))
            time = int(elem[1:])
            full_time += time
            data.append((level, time))

        return data

    @classmethod
    def detect_fill_interval(cls, data):
        _data = data
        while True:
            hist, bin_edges = np.histogram(_data, 20)
            edges = cls._remove_zero_interval(hist, bin_edges)
            if len(edges) == 1:
                _data = cls._split_into_intervals(data, edges)
            else:
                return edges

    @staticmethod
    def _remove_zero_interval(hist, bin_edges):
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
        if edge:
            edges.append(edge)
        return edges

    @staticmethod
    def _split_into_intervals(data, intervals):
        _data = []
        for interval in intervals:
            _data.append([elem for elem in data if interval[0] <= elem <= interval[1]])
        return _data

    @classmethod
    def _detect_bit_length(cls, data, intervals):
        _data = cls._split_into_intervals(data, intervals)

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

    def set_default_props(self, signature):
        for name in signature:
            prop = signature[name]
            if prop.get('default'):
                self.props[name] = prop['default']
            if self.di:
                self.props['di'] = self.di
            if self.cmd:
                self.props['cmd'] = self.cmd
