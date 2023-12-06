import time
from threading import Thread

import sounddevice as sd
import argparse

from pynput.keyboard import Key
from whisper_operator import WhisperOperator
from mic_recorder import Microphone_Recorder, RATE

class AppLauncher:

    __args: argparse.Namespace
    __parser: argparse.ArgumentParser
    __mic_recorder: Microphone_Recorder
    __whisper_operator: WhisperOperator
    __mic_thread: Thread | None

    def __init__(self, args : argparse.Namespace, parser: argparse.ArgumentParser):
        self.__args = args
        self.__parser = parser

        self.__mic_recorder = Microphone_Recorder()
        self.__whisper_operator = WhisperOperator()
        self.__mic_thread: Thread | None = None

    def run(self):
        try:
            self.__recursion_input(target_device=(1 if self.__args.device is None else self.__args.device))

        except KeyboardInterrupt:
            self.__mic_recorder.stop()
            print('\nRecording finished')
            self.__parser.exit(0)

        except Exception as e:
            self.__parser.exit(type(e).__name__ + ': ' + str(e))

    def __transcribe(self):
        transcription = self.__whisper_operator.process(sample_size=RATE, data=self.__mic_recorder.data)
        print(transcription)

    def __recursion_input(self, target_device: str | int):
        value = input("Press {} To Continue".format("K" if self.__mic_recorder.is_playing else "P"))

        # Stop Recording
        if value == "k":
            self.__mic_recorder.stop()

            if self.__mic_thread is not None:
                self.__mic_thread.join()
            self.__mic_thread = None
            print("MIC Stop")
            self.__transcribe()

        # Start Recording
        if value == "p" and self.__mic_recorder.is_playing is not True:
            self.__mic_thread = Thread(target=self.__mic_recorder.record, args=[target_device])
            self.__mic_thread.start()
            time.sleep(0.1)

        self.__recursion_input(target_device)

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')

args = parser.parse_args(remaining)

app_launcher = AppLauncher(args, parser)
app_launcher.run()
