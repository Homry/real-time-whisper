import io
import struct

import numpy as np
import socketio
import whisper
from scipy.io.wavfile import write
import soundfile as sf

sio = socketio.Client()

sio.connect('ws://127.0.0.1:5000', transports=['websocket'])

model = whisper.load_model("medium")
model = model.to('cuda:0')


class Queue:
    def __init__(self):
        self.data = []

    def add(self, data):
        self.data.append(data)

    def pop(self):
        if not self.empty():
            return self.data.pop(0)

    def empty(self):
        return True if len(self.data) == 0 else False


q = Queue()


@sio.on('voice')
def process(data):
    # audio = np.frombuffer(data, dtype=np.float32)
    # audio = np.nan_to_num(audio)  # Заменяет все значения nan на 0
    q.add(data)


def convert_bytearray_to_wav_ndarray(input_bytearray: bytes, sampling_rate=16000):
    bytes_wav = bytes()
    byte_io = io.BytesIO(bytes_wav)
    write(byte_io, sampling_rate, np.frombuffer(input_bytearray, dtype=np.int16))
    output_wav = byte_io.read()
    output, samplerate = sf.read(io.BytesIO(output_wav))
    write('batch.wav', sampling_rate, output)
    return 'batch.wav'

while True:
    if not q.empty():
        data = q.pop()

        result = model.transcribe(np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0, language='ru')
        print(result["text"])

