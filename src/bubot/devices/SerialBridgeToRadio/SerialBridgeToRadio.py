from bubot.devices.Device.Device import Device
from bubot.devices.Device.QueueMixin import QueueMixin
from .__init__ import __version__ as device_version
from bubot.ExtException import ExtException
from bubot.devices.SerialBridgeToRadio.BinarySignal import BinarySignal
from serial_asyncio import open_serial_connection
import asyncio


# _logger = logging.getLogger(__name__)


class SerialBridgeToRadio(Device, QueueMixin):
    version = device_version
    file = __file__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.transmit_queue = asyncio.Queue()
        self.receive_queue = asyncio.Queue()
        self.transmit_queue_worker = None
        self.receive_queue_worker = None
        self.reader = None
        self.writer = None
        self.receiver_task = None
        self.radio_drivers = None

    async def on_pending(self):
        self.radio_drivers, schemas = self.find_drivers(rt='bubot.radio.con')
        await self.connect()
        self.receiver_task = asyncio.ensure_future(self.receiver())
        self.transmit_queue_worker = asyncio.ensure_future(self.queue_worker(
            self.transmit_queue,
            'transmit_queue'
        ))
        self.receive_queue_worker = asyncio.ensure_future(self.queue_worker(
            self.receive_queue,
            'receive_queue'
        ))
        await super().on_pending()
        pass

    async def connect(self):
        host = self.get_param('/oic/con', 'host')
        self.log.debug('connect to serial {}'.format(host))
        self.reader, self.writer = await open_serial_connection(
            url=host,
            baudrate=self.get_param('/oic/con', 'baudRate')
        )

    async def receiver(self):
        self.log.debug('receiver begin')
        while True:
            try:
                data = await self.reader.readline()
                data = data.decode().strip()
                self.log.debug('received signal: {}'.format(data))
                self.receive_queue.put_nowait((self.signal_handler(data), None))
            except Exception as e:
                self.log.error(str(e))
                continue

    async def signal_handler(self, raw):
        self.log.debug('signal decoding: {}'.format(raw))
        try:
            signal = BinarySignal()
            try:
                data = signal.decode(raw)
                self.log.debug('signal decoded: {}'.format(data))
                detect = []
                for driver in self.radio_drivers:
                    try:
                        _driver = self.radio_drivers[driver]['driver'].detect_signal(signal)
                        if _driver:
                            detect.append(_driver)
                    except Exception as e:
                        continue
                if len(detect) > 1:
                    self.log.warning('multi detect for signal {}'.format(data))
                if detect:
                    signal = detect[0]

                await self.notify('/radio_msg', signal.props)
            except KeyError as e:
                self.log.warning('{0} (signal: {1})'.format(str(e), raw))
            except Exception as e:
                self.log.error('signal decode: {0} (signal: {1})'.format(str(e), raw))
        except KeyError as e:
            self.log.warning('{0} (signal: {1})'.format(str(e), raw))

    async def transmitter(self, data):
        try:
            raw = 'B{}E'.format(data).encode()
            for i in range(3):
                res = self.writer.write(raw)
            pass
            return
        except KeyError as key:
            self.log.error('Не указан обязательный параметр {}'.format(key))
            raise Exception('Не указан обязательный параметр {}'.format(key))
        except asyncio.TimeoutError:
            self.log.error('Timeout')
            raise ExtException(9001) from None
        except Exception as e:
            self.log.error(e)
            raise ExtException(e, action='execute')

    async def on_update_radio_msg(self, message):
        result = await self.execute_in_queue(
            self.transmit_queue,
            self.transmitter(
                message.cn,
            ), name='execute')
        return result
