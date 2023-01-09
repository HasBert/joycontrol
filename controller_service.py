#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os

from aioconsole import ainput

import joycontrol.debug as debug
from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server
from joycontrol.nfc_tag import NFCTag

logger = logging.getLogger(__name__)


class ControllerService:

    def __init__(self):
        self.controller_state = None
        self.transport = None
        self.protocol = None

    async def close(self):
        logger.info('Stopping communication...')
        await self.transport.close()
        self.transport = None

    async def connect_controller(self, controller_name):
        # Get controller name to emulate from arguments
        controller = Controller.from_arg(controller_name)

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
                                                          interactive=True)

            self.transport = transport
            self.controller_state = protocol.get_controller_state()
