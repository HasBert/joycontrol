import logging

from typing import Union
from fastapi import FastAPI, HTTPException
from controller_service import ControllerService
from argparse import Namespace
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

app = FastAPI()

controllerService = ControllerService()


@app.get("/")
def read_root():
    return RedirectResponse('docs', status_code=303)


@app.get("/joymon/connect")
async def connect_controller(q: Union[str, None] = None):
    controller_name = 'PRO_CONTROLLER'
    args = Namespace(controller=controller_name,
                     spi_flash=None,
                     reconnect_bt_addr="auto",
                     log=None,
                     device_id=None)
    # last = controllerService.get_last_switch_address()
    # if last is not None:
    #     args.reconnect_bt_addr()

    try:
        await controllerService.connect(args)
        return {"status": "ok"}
    except OSError as err:
        raise HTTPException(status_code=500, detail=err.args)


@app.get("/joymon/disconnect")
async def disconnect_controller():
    await controllerService.close()
    return {"status": "ok"}


@app.post("/joymon/start/acetournament")
async def start_acetournament():
    await controllerService.test_pokemon()
    return {"status": "ok"}


@app.post("/joymon/stop")
async def stop_action():
    await controllerService.stop_current_action()
    return {"status": "ok"}
