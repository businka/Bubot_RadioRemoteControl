import serial
import time
from BinarySignal import BinarySignal
import unittest
from Dooya import Dooya

Dooya.addresses.update({
    'Кабинет левая':  '9a6d36d36db6d34db6924d26',  # 4d
    'Кабинет правая': '9a6d36d34db6d34db6924d26',
    'Спальня левая':  '9b4924d36db6da4d24924d26',
    'Спальня правая': '9b4924d34db6da4d24924d26',
    'Детская левая': '9a6d36d36db6934934924d26',
    'Детская правая': '9a6d36d34db6934934924d26',
    'Кухня левая': '9a69269369a4d24d24926926',
    'Кухня правая': '9a69269369a4d24d24926934',
    'Столовая балкон левая': '9a69269369a4d24d24926936',
    'Столовая балкон правая': '9a69269369a4d24d249269a4',
    'Диван левая': '9a69269369a4d24d249269a6',
    'Диван правая': '9a69269369a4d24d249269b4',
})


class TestDooya(unittest.TestCase):
    ser = None

    def open_port(self):
        self.ser = serial.Serial('COM3', 115200, timeout=1)
        if not self.ser.is_open:
            raise Exception('port not open')
        pass

    def tearDown(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def test_create_command(self):
        command = 'up'
        device = {
            'Кабинет левая': '9a6d36d36db6d34db6924d26'
        }

    def test_receiver(self):
        self.open_port()
        while True:
            while self.ser.inWaiting():
                data = self.ser.readline().decode()
                pass
                # if not data:
                #     time.sleep(0.01)
                #     continue
                try:
                    signal = BinarySignal()
                    try:
                        res = signal.decode(data)
                    except Exception as e:
                        print('signal decode err', e)
                        continue
                    if res:
                        res2 = signal.detect()
                        if len(res2) == 1:
                            print(res2[0]['device'])
                        else:
                            print('{0:x}'.format(res))
                    else:
                        print(data)

                except KeyError as e:
                    print('err', str(e), data)

    def test_transmitter(self):
        # data = '111111111111111111000001000111010001110111010001110111011101000111011101110111011101110111010001110100011101110111011101000100010001000111010001000111010001110100011101000111010001110'
        # size_bit = 268
        data = '11111111111110000100110100110110100110110110100110110110110110110110100110100110110110110100100100100110100100110100100100110100100100110'
        size_bit = 353
        signal = ''
        h = False
        size = 8000
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
                # signal += 'L8000;'
        signal = 'BH300;{0}L20000;E'.format(signal)
        # BL8000;H4589;L1412;H353;L706;H706;L353;H353;L706;H706;L353;H706;L353;H353;L706;H706;L353;H706;L353;H706;L353;H353;L706;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H353;L706;H706;L353;H353;L706;H706;L353;H706;L353;H706;L353;H706;L353;H353;L706;H353;L706;H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H353;L706;H706;L20000;E

        # BL8000;H4589;L1412;H353;L706;H706;L353;H353;L706;H706;L353;H706;L353;H353;L706;H706;L353;H706;L353;H706;L353;H353;
        # L706;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H353;L706;H706;L353;H353;L706;H706;L353;
        # H706;L353;H706;L353;H706;L353;H353;L706;H353;L706;H353;L706;H353;L706;H706;L353;
        # H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H353;L706;H706;L20000;E
        self.open_port()
        print('write', self.ser.write(signal.encode()))
        transmit = False
        i = 0
        while i < 5:
            while self.ser.inWaiting():
                data = self.ser.readline()
                print('read ', data)
                if data:
                    print('read ', data)
                    if data == b'Transmit complete \r\n':
                        transmit = False
                else:
                    print('write', self.ser.write(signal.encode()))
                    transmit = True
                    i += 1

    def test_detect(self):
        a = [
            (
                '100110100110110100110110110100110110110110110110110100110100110110110110100100100100110100100110100100110110100100110110',
                'Вниз кабинет'),
            (
                '100110100110110100110110110100110100110110110110110100110100110110110110100100100100110100100110100100110110100100110110',
                'ВнизКабинет 2'),
            (
                '100110100110110100110110110100110100110110110110110100110100110110110110100100100100110100100110100100100110100100100110',
                ' Вверхкабинет 2'),
            (
                '100110100110110100110110110100110110110110110110110100110100110110110110100100100100110100100110100100100110100100100110',
                ' Вверхкабинет'),
            (
                '100110100110110100110110110100110110110110110110110100110100110110110110100100100100110100100110100110100110100110100110',
                ' стопкабинет 1'),
            (
                '100110100110110100110110110100110100110110110110110100110100110110110110100100100100110100100110100110100110100110100110',
                ' стопкабинет 2'),
            (
                '100110100110110100110110110100110110110110110110100100110100100100110100100100100100110100100110100110100110100110100110',
                ' стопваня 1'),
            (
                '100110100110110100110110110100110100110110110110100100110100100100110100100100100100110100100110100110100110100110100110',
                ' стопваня 2'),
            (
                '100110100110100100100110100100110110100110100100110100100100110100100100100100100110100100100100100110100110100110100110',
                ' стоп мн 0'),
            (
                '100110100110100100100110100100110110100110100100110100100100110100100100100100100110100100100110100110100110100110100110',
                ' стоп мн 1'),
            (
                '100110100110100100100110100100110110100110100100110100100100110100100100100100100110100100110100100110100110100110100110',
                ' стоп мн 2'),
        ]

        for elem in a:
            sig = int(elem[0], base=2)
            result = BinarySignal(data=sig).detect()
            if len(result) == 1:
                print(result[0]['device'])
            else:
                print('{0:x}'.format(sig), elem[1])

        pass

    def test_detect_interval(self):
        source = 'L12000;H331;L8751;H4729;L1471;H333;L717;H712;L387;H326;L727;H716;L351;H724;L381;H333;L727;H700;L376;H712;L361;H707;L374;H347;L733;H699;L374;H705;L362;H699;L408;H677;L407;H656;L403;H683;L379;H686;L433;H291;L743;H703;L366;H336;L751;H677;L415;H664;L417;H681;L401;H675;L413;H293;L742;H322;L763;H327;L726;H339;L754;H695;L381;H329;L760;H312;L743;H696;L413;H292;L769;H686;L375;H327;L737;H696;L391;H337;L754;H671;L374;H329;L793;H659;L12000;'
        signal = BinarySignal()
        result = signal.decode(source)
        result1 = signal.detect()
        pass
