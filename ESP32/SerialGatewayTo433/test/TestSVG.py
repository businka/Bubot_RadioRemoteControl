import unittest
from BinarySignal import BinarySignal
from SvgGraphSignal import SvgGraphSignal
import asyncio
import serial


class TestSVG(unittest.TestCase):
    def test_create_svg(self):
        with(open('./data/stop.dooya.2.txt', 'r', encoding='utf-8')) as file:
            data = file.readlines()
        SvgGraphSignal().create_graph(data[0])
        pass

    def test_encpde_up(self):
        res = SvgGraphSignal().encode('0001')

    def test_decode(self):
        with(open('./data/stop.dooya.2.txt', 'r', encoding='utf-8')) as file:
            data = file.readlines()
        with(open('./data/stop.dooya.3.txt', 'w', encoding='utf-8')) as file:
            for elem in data:
                try:
                    res = BinarySignal().decode(elem)
                except Exception as e:
                    res = str(e) + "===" + elem
                file.write(res + "\n")
        pass

    def test_send(self):
        class Output(asyncio.Protocol):

            def __init__(self):
                super().__init__()
                self._transport = None

            def connection_made(self, transport):
                self._transport = transport
                print('port opened', self._transport)
                self._transport.serial.rts = False
                res = SvgGraphSignal().encode(49071, '0001')
                self._transport.write(res[0])
                self._transport.write(res[0])
                self._transport.write(res[0])
                self._transport.write(res[1])
                self._transport.write(res[1])
                self._transport.write(res[1])

            def data_received(self, data):
                print(data)
                svg = SvgGraphSignal()
                svg.prepare_data(data.decode())
                if svg.data:
                    svg.decode_dooya_variant1()
                # print('data received', repr(data))
                # if b'\n' in data:
                #     self._transport.close()

            def connection_lost(self, exc):
                print('port closed')
                self._transport.loop.stop()

            def pause_writing(self):
                print('pause writing')
                print(self._transport.get_write_buffer_size())

            def resume_writing(self):
                print(self._transport.get_write_buffer_size())
                print('resume writing')

        loop = asyncio.get_event_loop()
        coro = serial1.create_serial_connection(loop, Output, 'COM5', baudrate=115200)
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()
