import logging

from typing import Union

from fastapi import FastAPI

from controller_service import ControllerService

logger = logging.getLogger(__name__)

app = FastAPI()

controllerService = ControllerService()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/joymon/connect/{controller_name}")
async def connect_controller(controller_name: str, q: Union[str, None] = None):
    await controllerService.connect_controller(controller_name)
    return {"controller_name": controller_name, "q": q}


@app.get("/joymon/disconnect")
async def disconnect_controller(item_id: int, q: Union[str, None] = None):
    await controllerService.close()
    return {"item_id": item_id, "q": q}
