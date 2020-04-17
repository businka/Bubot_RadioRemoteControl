import async_serial
import asyncio

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
from SvgGraphSignal import SvgGraphSignal
from BinarySignal import BinarySignal


if __name__ == '__main__':

    class Reader:
        def __init__(self):
            self.current_msg = ''

        def read(self, data):
            _data = data.decode('utf-8').split('\n')
            size = len(_data)
            for i, elem in enumerate(_data):
                if not elem:
                    if self.current_msg:
                        self.on_message(self.current_msg)
                        self.current_msg = ''
                    continue
                if i == 0:
                    self.current_msg += elem
                    if size > 1:
                        self.on_message(self.current_msg)
                        self.current_msg = ''
                        continue
                elif size - 1 > i:
                    self.on_message(elem)
                    continue
                else:
                    self.current_msg += elem
                    continue

        def on_message(self, data):
            try:
                res = BinarySignal().decode(data)
                print(res)
            except KeyError as e:
                print(self.current_msg)
                print(str(e))


    class Output(asyncio.Protocol):

        def __init__(self, test):
            super().__init__()
            self._transport = None
            self.test = test

        def connection_made(self, transport):
            self._transport = transport
            print('port opened', self._transport)
            # self._transport.serial.rts = False
            # self._transport.write(b'Hello, World!\n')

        def data_received(self, data):
            self.test.read(data)
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
    coro = async_serial.create_serial_connection(loop, Output(Reader()), 'COM3', baudrate=115200, timeout=10)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
