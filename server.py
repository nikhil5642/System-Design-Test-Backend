import asyncio
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

from polling import pollingApp
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
app.mount("/polling",pollingApp)
origins = ["*"]

class TextData(BaseModel):
    text: str

class EmailData(BaseModel):
    email: str
    content: str


# Adding middleware to ensure the connection is kept alive
class KeepAliveMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Connection"] = "keep-alive"
        return response

app.add_middleware(KeepAliveMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred"},
    )
    
    
@app.get("/sendText")
async def send_text():
    logging.info("Processing Get request on /sendText")
    return {"message": "Text received successfully"}

@app.put("/sendEmail")
async def send_email(data: EmailData):
    logging.info("Processing PUT request on /sendEmail")
    received_email = data.email
    received_content = data.content
    return {"message": "Email sent successfully", "received_email": received_email, "content": received_content}

async def fake_data_stream():
    for i in range(10):  # Simulate sending 100 messages
        yield f"data: Event {i}\n\n"
        await asyncio.sleep(1)  # Pause for a second between messages  # noqa: F821

@app.get("/stream")
async def stream():
    return StreamingResponse(fake_data_stream(), media_type="text/event-stream")  # noqa: F821

@app.get("/download-file")
async def download_file():
    file_path = "DappLinker Polygon Grant Submission.pdf.zip"  # Specify the path to the large file
    def file_streamer():
        with open(file_path, mode="rb") as file:
            while chunk := file.read(4096):  # Read and stream in chunks of 4KB
                yield chunk

    headers = {
        "Content-Disposition": f"attachment; filename={file_path}"
    }
    return StreamingResponse(file_streamer(), headers=headers)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive messages and process them
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
    finally:
        # Safely close the WebSocket connection
        if not websocket.client_state.value == "CLOSED":
            await websocket.close()
        print("WebSocket connection safely closed")
