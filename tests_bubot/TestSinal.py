import unittest
from bubot.devices.SerialBridgeToRadio.BinarySignal import BinarySignal
from bubot.devices.DooyaCurtain433.DooyaCurtain433 import DooyaCurtain433


class TestSignal(unittest.TestCase):
    def test_signal_decode(self):
        data = 'L8000;H4139;L38;H658;L171;H266;L171;H989;L216;H256;L216;H402;L270;H1413;L198;H2528;\r\n'
        signal = BinarySignal()
        res = signal.decode(data)
        pass

    def test_signal_decode_encode_dooya(self):
        # data = 'L8000;H4724;L1433;H375;L695;H735;L348;H370;L703;H726;L353;H718;L366;H352;L717;H720;L359;H716;L360;H714;L363;H353;L718;H716;L366;H354;L713;H720;L361;H714;L368;H707;L364;H710;L369;H706;L370;H348;L719;H715;L368;H351;L718;H716;L363;H713;L364;H709;L369;H708;L367;H350;L720;H359;L720;H357;L712;H366;L714;H717;L361;H357;L712;H366;L711;H719;L358;H362;L715;H717;L362;H356;L711;H722;L360;H357;L715;H720;L363;H356;L713;H720;'
        data = 'L8000;H4730;L1433;H355;L710;H710;L355;H355;L710;H710;L355;H710;L355;H355;L710;H710;L355;H710;L355;H710;L355;H355;L710;H710;L355;H355;L710;H710;L355;H710;L355;H710;L355;H710;L355;H710;L355;H355;L710;H710;L355;H355;L710;H710;L355;H710;L355;H710;L355;H710;L355;H355;L710;H355;L710;H355;L710;H355;L710;H710;L355;H355;L710;H355;L710;H710;L355;H355;L710;H355;L710;H355;L710;H710;L355;H355;L710;H355;L710;H355;L710;H710;L2000;'
        signal = BinarySignal()
        data = signal.decode(data)
        res = DooyaCurtain433.detect_signal(signal)
        self.assertEqual(res.n, 'Dooya DC1651')
        signal2 = BinarySignal(di=res.di, cmd=res.cmd, n=res.n)
        raw = signal2.encode(DooyaCurtain433.signature)
        self.assertEqual(signal2.data, data)
        pass

    def test_signal_encode(self):
        signal = BinarySignal(didata=int('{0}{1}'.format(self.get_param('di'), self.commands['up'])))
