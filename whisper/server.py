import numpy as np
import socketio
import uvicorn
import pyaudio
from fastapi import FastAPI

import struct

sio = socketio.AsyncServer(
    async_mode="asgi", cors_credentials=True, cors_allowed_origins="*"
)



app = FastAPI(title="test")


@app.get('/')
async def get():
    print('here')
    sample_rate = 16000
    duration = 5
    chunk_size = 16000 * duration
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=chunk_size)
    for i in range(100):
        data = stream.read(chunk_size)
        await sio.emit('voice', data)







socket = socketio.ASGIApp(sio, app)

@sio.event
def connect(sid, data):
    print('connect')


uvicorn.run(
    socket,
    forwarded_allow_ips="*",
    host='127.0.0.1',
    port=5000,
)