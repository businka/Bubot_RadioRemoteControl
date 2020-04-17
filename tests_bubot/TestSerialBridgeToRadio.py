import unittest
import asyncio
from bubot.devices.Console.Console import Console
from bubot.devices.SerialBridgeToRadio.SerialBridgeToRadio import SerialBridgeToRadio as BridgeDevice
from bubot.devices.DooyaCurtain433.DooyaCurtain433 import DooyaCurtain433 as Device
from bubot.OcfMessage import OcfRequest
from bubot.TestHelper import async_test, wait_run_device, get_config_path
import logging


class TestSerialBridgeToRadio(unittest.TestCase):
    config = {
        '/oic/d': {
            'di': '9a6d36d34db6d34db6924d26'
        },
        '/oic/con': {
            'bridge': dict(href='/radio_msg'),
            'logLevel': "debug",
            'udpCoapPort': 17771,
            'udpCoapIPv4': False,
            'udpCoapIPv6': True
        }

    }

    @async_test
    async def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.config_path = get_config_path(__file__)
        pass

    @async_test
    async def test_init(self):
        self.assertIn('/light', self.device.data)
        self.assertListEqual(self.device.data['/light']['rt'], ['oic.r.switch.binary', 'oic.r.light.brightness'])

    @async_test
    async def test_on_init(self):
        await self.device.on_init()
        pass

    @async_test
    async def test_power(self):
        value = True
        console_device = Device.init_from_file('Console', '4')
        console_task = await wait_run_device(console_device)

        bridge_device = Device.init_from_file('SerialBridgeToRadio', '3')
        bridge_task = await wait_run_device(bridge_device)

        self.config['/oic/con']['bridge']['anchor'] = bridge_device.link['anchor']
        self.config['/oic/con']['bridge']['eps'] = bridge_device.link['eps']
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)

        # подписываемся на все данные приятые из эфира
        # message = OcfRequest(op='retrieve', fr=console_device.link, to=dict(href='/radio_msg'), obs=0)
        link = bridge_device.get_link('/radio_msg')
        await console_device.observe(link, console_device.on_update_console)
        message = OcfRequest(op='update', to=dict(href='/curtain'), cn=dict(openLevel=100))
        # while True:
        result = await self.device.on_post_request(message)
        # await asyncio.sleep(5)
        pass

        await asyncio.sleep(999)
        # await self.power(True)
        # await self.power(False)

    @async_test
    async def test_dooya_signal_handler(self):
        signal1 = "L8000;H4724;L1437;H362;L711;H724;L357;H359;L712;H724;L353;H718;L363;H354;L717;H718;L360;H713;L365;H710;L363;H355;L718;H718;L363;H709;L369;H708;L364;H711;L365;H710;L365;H709;L370;H705;L375;H340;L728;H711;L368;H350;L720;H703;L398;H676;L392;H690;L377;H698;L379;H340;L729;H352;L719;H359;L717;H361;L708;H725;L357;H359;L714;H365;L709;H720;L361;H356;L717;H720;L356;H360;L714;H718;L362;H354;L718;H719;L362;H355;L718;H714;"
        bridge_device = BridgeDevice.init_from_file('SerialBridgeToRadio', '3')
        result = bridge_device.signal_handler(signal1)
        pass

    @async_test
    async def test_update_radio_msg(self):
        # raw = 'L8000;H4589;L1412;H353;L706;H706;L353;H353;L706;H706;L353;H706;L353;H353;L706;H706;L353;H706;L353;H706;L353;H353;L706;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H706;L353;H353;L706;H706;L353;H353;L706;H706;L353;H706;L353;H706;L353;H706;L353;H353;L706;H353;L706;H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H353;L706;H706;L353;H353;L706;H353;L706;H353;L706;H706;L20000;'
        raw = 'L8000;H4730;L1433;H355;L710;H710;L355;H355;L710;H710;L355;H710;L355;H355;L710;H710;L355;H710;L355;H710;L355;H355;L710;H710;L355;H355;L710;H710;L355;H710;L355;H710;L355;H710;L355;H710;L355;H355;L710;H710;L355;H355;L710;H710;L355;H710;L355;H710;L355;H710;L355;H355;L710;H355;L710;H355;L710;H355;L710;H710;L355;H355;L710;H355;L710;H710;L355;H355;L710;H355;L710;H355;L710;H710;L355;H355;L710;H355;L710;H355;L710;H710;L2000;'
        cn = dict(raw=raw)
        bridge_device = Device.init_from_file('SerialBridgeToRadio', '3')
        bridge_task = await wait_run_device(bridge_device)
        message = OcfRequest(op='update', to=dict(href='/radio_msg'), cn=cn)
        result = await bridge_device.on_post_request(message)
        # self.assertEqual(result['openLevel'], 2)
        bridge_task.cancel()
        pass

    @async_test
    async def test_update_open_level(self):
        bridge_device = Device.init_from_file('SerialBridgeToRadio', '3')
        bridge_task = await wait_run_device(bridge_device)
        self.config['/oic/con']['bridge']['anchor'] = bridge_device.link['anchor']
        self.config['/oic/con']['bridge']['eps'] = bridge_device.link['eps']
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='update', to=dict(href='/curtain'), cn=dict(openLevel=100))
        result = await self.device.on_post_request(message)

        bridge_task.cancel()
        device_task.cancel()

    @async_test
    async def test_update_switch(self):
        value = False
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        modbus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        message = OcfRequest(op='update', to=dict(href='/power'), cn=dict(value=value))
        result = await self.device.on_post_request(message)
        self.assertEqual(result['value'], value)
        modbus_task.cancel()
        device_task.cancel()
        pass

    @async_test
    async def test_find_devices(self):
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.action_find_devices()
        pass

    @async_test
    async def test_is_device(self):
        brightness = 60
        modbus_device = ModbusDevice.init_from_config(self.modbus_config, path=self.config_path)
        mobus_task = await wait_run_device(modbus_device)
        self.config['/oic/con']['master'] = modbus_device.link
        self.device = Device.init_from_config(self.config, path=self.config_path)
        device_task = await wait_run_device(self.device)
        res = await self.device.modbus.is_device()
        self.assertTrue(res)
        pass

    @async_test
    async def test_echo_get_light_baseline(self):
        await self.device.run()
        from aio_modbus_client.ModbusProtocolEcho import ModbusProtocolEcho
        while self.device.get_param('/oic/con', 'status_code') == 'load':
            await asyncio.sleep(0.1)
        self.device.modbus.protocol = ModbusProtocolEcho({
            '\x00\x02\x00\x01': '\x01\x00\x01'
        })
        result = await self.device.modbus.read_param('level_blue')
        pass

    @async_test
    async def test_get_light_baseline(self):
        main = await self.device.run()
        await main
        # while self.device.get_props('/oic/con', 'status_code') == 'load':
        #     await asyncio.sleep(0.1)
        result = await self.device.modbus.read_param('level_blue')
        pass

    @async_test
    def test_get_light1_baseline(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light'))
        result = self.device.on_get_request(message)
        pass

    @async_test
    def test_set_light_baseline(self):
        self.device = Device.init_from_config(self.config)
        data = dict(value=True, brightness=100)
        message = OcfRequest(**dict(operation='update', uri_path=['light'], data=data))
        self.device.on_init()
        result = self.device.on_post_request(message)
        self.assertDictEqual(result, data)

    @async_test
    def test_get_light_brightness(self):
        self.device = Device.init_from_config(None, dict(handler=Device.__name__, data=self.config))
        message = OcfRequest(**dict(operation='get', uri='/light', query={'rt': ['oic.r.light.brightness']}))
        self.device.on_get_request(message)

        # self.devices.run()
        pass

    @async_test
    async def test_run(self):
        await self.device.run()
        # result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_discovery(self):
        await self.device.run()
        result = await self.device.coap.discovery_resource()
        await asyncio.sleep(600)
        pass

    @async_test
    async def test_local_discovery(self):
        msg = OcfRequest(**dict(
            uri_path=['oic', 'res'],
            operation='get'
        ))
        res = self.device.on_get_request(msg)
        await asyncio.sleep(600)
        pass
