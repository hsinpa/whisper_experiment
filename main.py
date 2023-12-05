from threading import Thread

import sounddevice as sd
import argparse

from pynput.keyboard import Key

from mic_recorder import Microphone_Recorder
from pynput import keyboard

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def recursion_input(mic: Microphone_Recorder, target_device: str):
    value = input("Press {} To Continue".format("K" if mic.is_playing else "P"))

    #Stop Recording
    if value == "k":
        mic.stop()
        print("MIC Stop")

    #Start Recording
    if value == "p" and mic.is_playing is not True:
        t = Thread(target=mic.record, args=[target_device])
        t.start()

    recursion_input(mic, target_device)

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
mic_recorder = Microphone_Recorder()

try:
    print(args.device)
    recursion_input(mic=mic_recorder, target_device=(1 if args.device is None else args.device))

except KeyboardInterrupt:
    mic_recorder.stop()
    print('\nRecording finished')
    parser.exit(0)

except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))