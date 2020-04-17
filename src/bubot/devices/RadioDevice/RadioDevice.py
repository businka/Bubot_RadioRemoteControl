import asyncio
from bubot.devices.Device.Device import Device
from bubot.DeviceLink import ResourceLink
import os
import json
from bubot.devices.SerialBridgeToRadio.BinarySignal import BinarySignal

# _logger = logging.getLogger(__name__)


class RadioDevice(Device):
    file = __file__

    signature = None
    bit_length = None
    bit_length_min = None
    bit_length_max = None
    signal_length_bit_min = None
    signal_length_bit_max = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serial_queue = asyncio.Queue()
        self.serial_queue_worker = None
        self.bridge = None
        self.link_bridge = None
        self.load_signature()

    async def check_connection_to_bridge(self):
        try:
            if await self.request('retrieve', self.link_bridge):
                return True
            return False
        except Exception:
            return False

    def set_bridge(self):
        self.link_bridge = self.get_param('/oic/con', 'bridge')
        # self.bridge = self.ModbusDevice(self.get_param('/oic/con', 'bridge'), ModbusProtocolOcf(self))

    async def on_pending(self):
        if not self.bridge:
            self.set_bridge()

        master = await self.check_connection_to_bridge()
        for i in range(1):  # пытаемся достучаться
            if not master:
                self.log.debug('waiting bridge')
                await asyncio.sleep(i + 1)
                master = await self.check_connection_to_bridge()

        if not master:
            link = ResourceLink.init_from_link(self.get_param('/oic/con', 'bridge'))
            link = await self.find_resource_by_link(link)
            if link:
                self.log.debug('bridge found')
                self.set_param('/oic/con', 'bridge', link.data)
                self.save_config()
                self.set_bridge()
            pass
        if master:
            await super().on_pending()

    @classmethod
    def detect_signal(cls, signal):
        if not cls.signature:
            cls.load_signature()
        return signal.detect_signal(cls.signature)

    @classmethod
    def load_signature(cls):
        config_path = '{0}/signature.json'.format(os.path.dirname(cls.file))
        cls.signature = BinarySignal.load_signature_from_file(config_path)
