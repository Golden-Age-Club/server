import socketio
import logging

logger = logging.getLogger(__name__)

# Create a Socket.IO server
# async_mode='asgi' is compatible with FastAPI
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Create an ASGI application
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    logger.info(f"SocketIO Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"SocketIO Client disconnected: {sid}")
