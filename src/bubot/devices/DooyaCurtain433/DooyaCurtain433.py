from .__init__ import __version__ as device_version
from bubot.devices.RadioDevice.RadioDevice import RadioDevice
from bubot.devices.SerialBridgeToRadio.BinarySignal import BinarySignal
import asyncio
from bubot.OcfMessage import OcfRequest
import logging


# _logger = logging.getLogger(__name__)


class DooyaCurtain433(RadioDevice):
    version = device_version
    file = __file__

    name = 'Dooya'

    async def on_update_curtain(self, message):
        new_level = message.cn.get('openLevel')
        current_level = self.get_param('/curtain', 'openLevel')
        change_level = new_level - current_level
        open_time = 20  # время полного открытия в секундах
        work_time = round(change_level * open_time / 100)
        if change_level > 0:  # вверх
            await self.send_cmd('up')
            if new_level < 100:
                await asyncio.sleep(work_time)
                await self.send_cmd('stop')
        elif change_level < 0:  # вниз
            await self.send_cmd('down')
            if new_level > 0:
                await asyncio.sleep(work_time)
                await self.send_cmd('stop')

        self.update_param('/curtain', 'openLevel', new_level)
        return message.cn

    def get_raw_radio_msg(self, cmd):
        signal = BinarySignal(di=self.get_device_id(), cmd=cmd)
        raw = signal.encode(self.signature)
        return raw

    async def send_cmd(self, cmd):
        raw = self.get_raw_radio_msg(cmd)
        result = await self.request('update', self.get_param('/oic/con', 'bridge'), dict(raw=raw))
        pass
