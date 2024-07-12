from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
import asyncio
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

pollingApp = FastAPI()
pollingApp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_store = []  # This will hold the data
request_queue = []  # This will keep track of incoming requests

@pollingApp.get("/poll")
async def poll():
    if data_store:
        return JSONResponse({"data": data_store.pop(0)})

    event = asyncio.Event()
    request_queue.append(event)
    try:
        await asyncio.wait_for(event.wait(), timeout=30)  # 30 seconds timeout
    except asyncio.TimeoutError:
        request_queue.remove(event)  # Clean up event from queue if it times out
        raise HTTPException(status_code=204, detail="No Content")

    return JSONResponse({"data": data_store.pop(0)})

@pollingApp.post("/data")
async def post_data(data: str):
    data_store.append(data)
    for event in request_queue:
        event.set()
    request_queue.clear()
    return {"message": "Data added"}
