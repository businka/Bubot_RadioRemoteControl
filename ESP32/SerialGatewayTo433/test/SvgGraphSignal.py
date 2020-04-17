from xml.etree import ElementTree as ET


class SvgGraphSignal:

    def __init__(self, **kwargs):
        self.x_0 = 20
        self.y_0 = 20
        self.x_max = 0
        self.y_max = 0
        self.signal_height = 20
        self.data = []
        self.scale = 100
        self.svg = None
        self.len_data = 0

    def prepare_data1(self, data):
        if data[0] not in ['L', 'H']:
            return
        self.x_max = 0
        self.y_max = self.signal_height + self.y_0 * 2
        _data = data.split(';')
        self.data = []
        time = 0
        for elem in _data:
            try:
                _time = int(elem[1:])
                self.data.append([elem[0:1], time, _time])
                time += _time
            except Exception as e:
                pass

        # while True:
        #     try:
        #         i += 1
        #         time = int(_data[i][1:])
        #     except ValueError:  # конец строки
        #         break
        #     self.data[i - 1][2] = time - self.data[i - 1][1]
        #     self.data.append([_data[i][0:1], time, 0])

        self.len_data = len(self.data)
        self.x_max = time / self.scale + self.x_0

    def prepare_data(self, data):
        if data[0] not in ['L', 'H']:
            return
        self.x_max = 0
        self.y_max = self.signal_height + self.y_0 * 2
        _data = data.split(';')
        self.data = []
        i = 0
        time = 0
        self.data.append([_data[i][0:1], int(_data[i][1:]), 0])
        while True:
            try:
                i += 1
                time = int(_data[i][1:])
            except ValueError:  # конец строки
                break
            self.data[i - 1][2] = time - self.data[i - 1][1]
            self.data.append([_data[i][0:1], time, 0])

        self.len_data = len(self.data)
        self.x_max = time / self.scale + self.x_0


    def create_graph(self, data):
        self.prepare_data(data)
        self.decode_dooya_variant1()
        # self.detect_clock_frequency(data)
        svg = ET.Element('svg', version='1.1', xmlns='http://www.w3.org/2000/svg')
        y0 = self.y_0
        # self.draw_legend_bearing(svg, self.data)
        self.draw_signal(svg)

        max_x = str(self.x_max + self.x_0 * 2)
        max_y = str(self.y_max + self.y_0 * 2)
        svg.attrib['viewBox'] = "0, 0, {x}, {y}".format(x=max_x, y=max_y)
        svg.attrib['height'] = max_y
        svg.attrib['width'] = max_x
        # svg.attrib['height'] = '100%'
        # svg.attrib['width'] = '100%'
        with open("sample.svg", "wb") as file:
            file.write(ET.tostring(svg))

    def draw_legend_bearing(self, svg, data, **kwargs):
        # first_signal = data[0][2]
        # first_data = data[0][5]
        bearing = data[0][2][2] / self.scale
        begin = 0 / self.scale
        # begin = (first_data[1] - int(str(first_data[1] / first_data[2]).split('.')[0]) * first_data[2]) / self.scale

        self.draw_grid(svg, (begin + self.x_0, self.x_max), (0, self.y_max), bearing)

    def draw_signal(self, svg, **kwargs):
        y0 = self.y_0
        scale = kwargs.get('scale', 100)
        yh = y0
        yl = self.signal_height + y0

        path = "M{x},{y1}".format(x=self.x_0, y1=yl)
        for elem in self.data:
            if elem[0] == 'L':
                x = elem[1] / scale + self.x_0
                path += "L{0},{1}V{2}".format(str(x), yh, yl)
            elif elem[0] == 'H':
                x = elem[1] / scale + self.x_0
                path += "L{0},{1}V{2}".format(str(x), yl, yh)

        ET.SubElement(svg, 'path', attrib={
            'd': path,
            'stroke': 'red',
            'stroke-width': '0.3',
            'fill': 'none'
        })

    def detect_clock_frequency(self, inaccuracy):
        interval = {}
        # TODO: в цикле увеличивать погрешность пока не останется допустимое количество вариантов
        for sign in self.data:
            if not sign[2]:
                continue
            found = False
            for value in interval:
                if value - inaccuracy <= sign[2] <= value + inaccuracy:
                    found = True
                    interval[value].append(sign[2])  # добавляем если уже есть такой интервал
            if not found:
                interval[sign[2]] = [sign[2]]

        average = {}
        for elem in interval:
            count = len(interval[elem])
            if count > 10:
                interval[elem] = sorted(interval[elem])[2:count-2]
                count = len(interval[elem])
            average[elem] = [round(sum(interval[elem]) / max(count, 1)), count]
        pass

    @staticmethod
    def draw_grid(svg, x, y, step):
        def draw_vert_line(width):
            ET.SubElement(svg, 'line', attrib={
                'x1': str(c),
                'y1': str(y[0]),
                'x2': str(c),
                'y2': str(y[1]),
                'stroke': 'grey',
                'stroke-width': str(width),
                'stroke-dasharray': "1"
            })

        c = x[0]
        i = 0
        while c <= x[1]:
            if i == 0 or i == 10:
                i = 0
                draw_vert_line(0.6)
                pass
            elif i == 5:
                draw_vert_line(0.4)
                pass
            else:
                draw_vert_line(0.1)
                pass
            i += 1
            c += step

    def decode_dooya_variant1(self):
        def detect1(x1, x2):
            if x1[0] == 'H' and x2[0] == 'L':
                if step - tolerance <= x1[2] <= step + tolerance:
                    # and (step*2-tolerance <= x2[2] <= step*2 + tolerance):
                    return '0'
                elif step * 2 - tolerance <= x1[2] <= step * 2 + tolerance:
                    # and (step-tolerance <= x2[2] <= step + tolerance):
                    return '1'
            raise Exception('Error HL')
        data = self.data
        step = data[3][2]
        tolerance = step / 3
        bit = step * 3
        result1 = ''
        result2 = ''
        x = 5
        while x < self.len_data - 2:
            result1 += detect1(data[x], data[x + 1])
            x += 2
        # print('`{0} {1} {2} {3} {4}'.format(
        #     result1[0:8],
        #     result1[8:16],
        #     result1[16:24],
        #     result1[24:32],
        #     result1[32:40]
        # ))
        dooya = {
            '0001': 'Up',
            '0011': 'Down',
            '0101': 'Stop',
            '1100': 'p2'
        }
        print('dooya id={0} action={1}'.format(int(result1[8:24], 2), dooya[result1[32:36]]))
        self.detect_clock_frequency(tolerance)
        pass

    def encode(self, id, cmd='0001'):
        '''
                 358   1075
        L 14344  40     13
        H 360    1
        L 8755   24
        H 4727   13
        L 1428   4
        data
        L 14344  40

        1 = H1 L2
        0 = H2 L1


        :param commands:
        :return:
        '''

        def encode_data_to_delta(data):
            one = 358
            double = 715
            _data = ''
            for elem in data:
                if elem == '0':
                    _data += 'H{1}L{0};'.format(double, one)
                elif elem == '1':
                    _data += 'H{0}L{1};'.format(double, one)
            return 'L14344;H358;L8755;H4727;L1428;{0}L4344;'.format(_data).encode()


        rev_cmd = cmd[::-1]
        _cmd = '01011011{id}00001001{cmd}{cmd}'.format(id=bin(id)[2:], cmd=cmd)
        _cmd2 = '01011011{id}00001001{cmd}{rev_cmd}'.format(id=bin(id)[2:], cmd=cmd, rev_cmd=rev_cmd)
        data1 = encode_data_to_delta(_cmd)
        data2 = encode_data_to_delta(_cmd)
        return (data1, data2)

# 1075
# 360
# 715
