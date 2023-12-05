import tempfile
import queue
import sys
import sounddevice as sd
import soundfile as sf
import argparse
import numpy  # Make sure NumPy is loaded before it is used in the callback

CHANNELS = 1              # Number of audio channels (1 for mono, 2 for stereo)
RATE = 16000              # Sample rate (samples per second)
CHUNK = 400              # Number of frames per buffer
RECORD_SECONDS = 5        # Duration of recording in seconds

class Microphone_Recorder:
    __random_file_name: str = ""
    __queue: queue.Queue = queue.Queue()

    is_playing: bool = False

    def __init__(self):
        self.__random_file_name = tempfile.mktemp(prefix='output/delme_rec_unlimited_', suffix='.wav', dir='')

    def __callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.__queue.put(indata.copy())

    def record(self, device_name: str):
        if self.is_playing:
            return

        self.__queue.empty()
        self.is_playing = True
        with sf.SoundFile(self.__random_file_name, mode='x', samplerate=RATE,
                          channels=CHANNELS, subtype="PCM_16") as file:
            with sd.InputStream(samplerate=RATE, device=device_name,
                                channels=CHANNELS, callback=self.__callback):
                # print('#' * 80)
                # print('press Ctrl+C to stop the recording')
                # print('#' * 80)
                while self.is_playing:
                    file.write(self.__queue.get())

    def stop(self):
        self.is_playing = False
        return self.__random_file_name