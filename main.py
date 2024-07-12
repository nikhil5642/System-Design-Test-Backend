import asyncio
from hypercorn.config import Config
import uvicorn
from hypercorn.asyncio import serve
from grpcServer import serveGRPC
def HTTP11Server():
    uvicorn.run("server:app", host="0.0.0.0", port=8000,reload=True,workers=4,timeout_keep_alive=True)

def HTTP20Server():
    config = Config()
    config.bind = ["0.0.0.0:8000"]  # Set the server to listen on all interfaces at port 8000
    config.use_reloader = True      # Enable auto-reloader for development
    config.h2 = True                # Enable HTTP/2
    config.h1 = False
    asyncio.run(serve("server:app", config))  # noqa: F821

def GRPCServer():
    serveGRPC()

if __name__ == "__main__":
    # HTTP20Server()
    # HTTP11Server()
    GRPCServer()