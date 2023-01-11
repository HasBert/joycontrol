#!/usr/bin/env python3
import logging
import os
import asyncio

from aioconsole import ainput

import joycontrol.debug as debug
from joycontrol import logging_default as log, utils
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

logger = logging.getLogger(__name__)


class ControllerService:

    def __init__(self):
        self.controller_state = None
        self.transport = None

        # lol
        self.last_switch_address = None
        self.is_controller_free = True

    def get_last_switch_address(self):
        return self.last_switch_address

    async def close(self):
        logger.info('Stopping communication...')
        await self.transport.close()
        self.transport = None

    async def test_pokemon(self):
        if self.controller_state.get_controller() != Controller.PRO_CONTROLLER:
            raise ValueError('This script only works with the Pro Controller!')

        # waits until controller is fully connected
        await self.controller_state.connect()

        # asyncio.ensure_future

        # user_input = asyncio.ensure_future(
        #     ainput(prompt='Starting to make $$$! Press <enter> to stop.')
        # )
        # push all buttons consecutively until user input
        while not self.is_controller_free:
            await button_push(self.controller_state, 'A')

            await asyncio.sleep(0.5)

        # await future to trigger exceptions in case something went wrong
        # await user_input

        await button_push(self.controller_state, 'X')
        await button_push(self.controller_state, 'A')

    def stop_current_action(self):
        self.is_controller_free = True

    async def connect(self, args):
        # check if root
        if not os.geteuid() == 0:
            raise PermissionError('Script must run as root!')

        # setup logging
        # log.configure(console_level=logging.ERROR)
        log.configure()

        # Get controller name to emulate from arguments
        controller = Controller.from_arg(args.controller)

        # parse the spi flash
        if args.spi_flash:
            with open(args.spi_flash, 'rb') as spi_flash_file:
                spi_flash = FlashMemory(spi_flash_file.read())
        else:
            # Create memory containing default controller stick calibration
            spi_flash = FlashMemory()

        with utils.get_output(path=args.log, default=None) as capture_file:
            # prepare the the emulated controller
            factory = controller_protocol_factory(
                controller, spi_flash=spi_flash, reconnect=args.reconnect_bt_addr)
            ctl_psm, itr_psm = 17, 19
            transport, protocol = await create_hid_server(factory, reconnect_bt_addr=args.reconnect_bt_addr,
                                                          ctl_psm=ctl_psm,
                                                          itr_psm=itr_psm, capture_file=capture_file,
                                                          device_id=args.device_id,
                                                          interactive=False)

            self.transport = transport
            # self.last_switch_address = transport.get_extra_info('peername')
            self.controller_state = protocol.get_controller_state()
            self.is_controller_free = False
