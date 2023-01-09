import logging

from typing import Union
from fastapi import FastAPI
from controller_service import ControllerService
from argparse import Namespace

logger = logging.getLogger(__name__)

app = FastAPI()

controllerService = ControllerService()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/joymon/connect/{controller_name}")
async def connect_controller(controller_name: str, q: Union[str, None] = None):

    args = Namespace(controller=controller_name,
                     spi_flash=None,
                     reconnect_bt_addr="auto",
                     log=None,
                     device_id=None)
    # last = controllerService.get_last_switch_address()
    # if last is not None:
    #     args.reconnect_bt_addr()

    await controllerService.connect_controller(args)
    return {"controller_name": controller_name, "q": q}


@app.get("/joymon/disconnect")
async def disconnect_controller():
    await controllerService.close()
    return {"status": "ok"}
