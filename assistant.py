import os
import random
import webbrowser
import pvporcupine
import simpleaudio as sa
from pvrecorder import PvRecorder
from rich import print
import vosk
import sys
from queue import Queue
import json
import struct
import config
from fuzzywuzzy import fuzz
import tts
import datetime
from num2words import num2words
import subprocess
import time
import threading
import tkinter as tk

from classes import animation_queue, MovingMan

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL, COMObject
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)

import openai
from gpytranslate import SyncTranslator

CDIR = os.getcwd()

# init translator
t = SyncTranslator()

# init openai
# openai.api_key = config.OPENAI_TOKEN

# PORCUPINE
porcupine = pvporcupine.create(
    access_key='H2JhXpfLdGYG2wMqvc61tipo0uKZQvwkEfA26CAQQe5n1y7zfZGneQ==',
    keywords=['jarvis'],
    sensitivities=[1]
)

# VOSK
model = vosk.Model("model_small")
samplerate = 16000
device = config.MICROPHONE_INDEX
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)


def gpt_answer(message):
    model_engine = "text-davinci-003"
    max_tokens = 128  # default 1024
    prompt = t.translate(message, targetlang="en")
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt.text,
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    translated_result = t.translate(completion.choices[0].text, targetlang="ru")
    return translated_result.text

def play(phrase, wait_done=True):
    global recorder
    filename = f"{CDIR}\\sound\\"

    if phrase == "greet":  # for py 3.8
        filename += f"greet{random.choice([1, 2, 3])}.wav"
    elif phrase == "ok":
        filename += f"ok{random.choice([1, 2, 3])}.wav"
    elif phrase == "not_found":
        filename += "not_found.wav"
    elif phrase == "thanks":
        filename += "thanks.wav"
    elif phrase == "run":
        filename += "run.wav"
    elif phrase == "stupid":
        filename += "stupid.wav"
    elif phrase == "ready":
        filename += "ready.wav"
    elif phrase == "off":
        filename += "off.wav"

    if wait_done:
        recorder.stop()

    wave_obj = sa.WaveObject.from_wave_file(filename)
    wave_obj.play()

    if wait_done:
        time.sleep(0.8)
        recorder.start()

def va_respond(voice: str):
    global recorder
    print(f"Распознано: {voice}")

    cmd = recognize_cmd(filter_cmd(voice))

    print(cmd)

    if len(cmd['cmd'].strip()) <= 0:
        return False
    elif cmd['percent'] < 70 or cmd['cmd'] not in config.VA_CMD_LIST.keys():
        if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:
            gpt_result = gpt_answer(voice)
            recorder.stop()
            tts.va_speak(gpt_result)
            time.sleep(1)
            recorder.start()
            return False
        else:
            play("not_found")
            time.sleep(1)
        return False
    else:
        execute_cmd(cmd['cmd'], voice)
        return True

def filter_cmd(raw_voice: str):
    cmd = raw_voice

    for x in config.VA_ALIAS:
        cmd = cmd.replace(x, "").strip()

    for x in config.VA_TBR:
        cmd = cmd.replace(x, "").strip()

    return cmd

def recognize_cmd(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in config.VA_CMD_LIST.items():
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt
    return rc

def execute_cmd(cmd: str, voice: str):
    if cmd == 'help':
        text = "Я вмію розказувати жарти, відкривати браузери, працювати офлайн, і багато чого іншого"
        tts.va_speak(text)
        animation_queue.put("jump")
        time.sleep(2)
        animation_queue.put("standart")

    elif cmd == 'open_browser':
        play("ok")
        animation_queue.put("jump")
        webbrowser.open("https://www.browser.com")
        time.sleep(1)
        animation_queue.put("standart")

    elif cmd == 'open_youtube':
        play("ok")
        animation_queue.put("jump")
        webbrowser.open("https://www.youtube.com")
        time.sleep(1)
        animation_queue.put("standart")
    elif cmd == 'open_google':
        play("ok")
        animation_queue.put("jump")
        webbrowser.open("https://www.google.com")
        time.sleep(1)
        animation_queue.put("standart")

    elif cmd == 'music':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Run music.exe'])
        play("ok")
        time.sleep(2)

    elif cmd == 'sound_off':
        play("ok", True)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)
        time.sleep(1)

    elif cmd == 'sound_on':
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0, None)
        play("ok")
        time.sleep(1)

    elif cmd == 'off':
        play("off", True)
        porcupine.delete()
        time.sleep(2)
        exit(0)

# Recorder setup and listening loop
recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
recorder.start()
print('Using device: %s' % recorder.selected_device)

print(f"Jarvis (v3.0) начал свою работу ...")
play("run")
time.sleep(0.5)

ltc = time.time() - 1000

def run_assistant():
    ltc = time.time() - 100
    while True:
        try:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                recorder.stop()
                play("greet", True)
                animation_queue.put("standart")
                print("Yes, sir.")
                recorder.start()
                ltc = time.time()

            while time.time() - ltc <= 10:
                pcm = recorder.read()
                sp = struct.pack("h" * len(pcm), *pcm)

                if kaldi_rec.AcceptWaveform(sp):
                    if va_respond(json.loads(kaldi_rec.Result())["text"]):
                        ltc = time.time()
                        
                    break
                
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

# while True:
#     try:
#         pcm = recorder.read()
#         keyword_index = porcupine.process(pcm)

#         if keyword_index >= 0:
#             recorder.stop()
#             play("greet", True)
#             print("Yes, sir.")
#             recorder.start()  # Prevent self-recording
#             ltc = time.time()

#         while time.time() - ltc <= 10:
#             pcm = recorder.read()
#             sp = struct.pack("h" * len(pcm), *pcm)

#             if kaldi_rec.AcceptWaveform(sp):
#                 if va_respond(json.loads(kaldi_rec.Result())["text"]):  # Передаємо animation_control
#                     ltc = time.time()

#                 break

#     except Exception as err:
#         print(f"Unexpected {err=}, {type(err)=}")
#         raise

def start_animation_window():
    root = tk.Tk()
    MovingMan(root, animation_queue)
    root.mainloop()

# Запуск асистента та анімації
if __name__ == "__main__":
    animation_thread = threading.Thread(target=start_animation_window)
    animation_thread.daemon = True
    animation_thread.start()

    run_assistant()







































# import os
# import random
# import webbrowser
# import pvporcupine
# import simpleaudio as sa
# from pvrecorder import PvRecorder
# from rich import print
# import vosk
# import sys
# import queue
# import json
# import struct
# import config
# from fuzzywuzzy import fuzz
# from classes import MovingMan
# from threading import Event
# import tts
# import datetime
# from num2words import num2words
# import subprocess
# import time
# import threading
# import tkinter as tk

# from ctypes import POINTER, cast
# from comtypes import CLSCTX_ALL, COMObject
# from pycaw.pycaw import (
#     AudioUtilities,
#     IAudioEndpointVolume
# )

# import openai
# from gpytranslate import SyncTranslator

# CDIR = os.getcwd()

# # init translator
# t = SyncTranslator()

# # init openai
# # openai.api_key = config.OPENAI_TOKEN

# # PORCUPINE
# porcupine = pvporcupine.create(
#     access_key='H2JhXpfLdGYG2wMqvc61tipo0uKZQvwkEfA26CAQQe5n1y7zfZGneQ==',
#     keywords=['jarvis'],
#     sensitivities=[1]
# )

# # VOSK
# model = vosk.Model("model_small")
# samplerate = 16000
# device = config.MICROPHONE_INDEX
# kaldi_rec = vosk.KaldiRecognizer(model, samplerate)
# q = queue.Queue()

# def gpt_answer(message):
#     model_engine = "text-davinci-003"
#     max_tokens = 128  # default 1024
#     prompt = t.translate(message, targetlang="en")
#     completion = openai.Completion.create(
#         engine=model_engine,
#         prompt=prompt.text,
#         max_tokens=max_tokens,
#         temperature=0.5,
#         top_p=1,
#         frequency_penalty=0,
#         presence_penalty=0
#     )

#     translated_result = t.translate(completion.choices[0].text, targetlang="ru")
#     return translated_result.text

# # Function to play sound based on phrases
# def play(phrase, wait_done=True):
#     global recorder
#     filename = f"{CDIR}\\sound\\"

#     if phrase == "greet":  # for py 3.8
#         filename += f"greet{random.choice([1, 2, 3])}.wav"
#     elif phrase == "ok":
#         filename += f"ok{random.choice([1, 2, 3])}.wav"
#     elif phrase == "not_found":
#         filename += "not_found.wav"
#     elif phrase == "thanks":
#         filename += "thanks.wav"
#     elif phrase == "run":
#         filename += "run.wav"
#     elif phrase == "stupid":
#         filename += "stupid.wav"
#     elif phrase == "ready":
#         filename += "ready.wav"
#     elif phrase == "off":
#         filename += "off.wav"

#     if wait_done:
#         recorder.stop()

#     wave_obj = sa.WaveObject.from_wave_file(filename)
#     wave_obj.play()

#     if wait_done:
#         time.sleep(0.8)
#         recorder.start()

# # Process the voice input and recognize commands
# def va_respond(voice: str):
#     global recorder
#     print(f"Распознано: {voice}")

#     cmd = recognize_cmd(filter_cmd(voice))

#     print(cmd)

#     if len(cmd['cmd'].strip()) <= 0:
#         return False
#     elif cmd['percent'] < 70 or cmd['cmd'] not in config.VA_CMD_LIST.keys():
#         if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:
#             gpt_result = gpt_answer(voice)
#             recorder.stop()
#             tts.va_speak(gpt_result)
#             time.sleep(1)
#             recorder.start()
#             return False
#         else:
#             play("not_found")
#             time.sleep(1)
#         return False
#     else:
#         execute_cmd(cmd['cmd'], voice)
#         return True

# # Filter and process raw voice commands
# def filter_cmd(raw_voice: str):
#     cmd = raw_voice

#     for x in config.VA_ALIAS:
#         cmd = cmd.replace(x, "").strip()

#     for x in config.VA_TBR:
#         cmd = cmd.replace(x, "").strip()

#     return cmd

# # Recognize and return the closest matching command
# def recognize_cmd(cmd: str):
#     rc = {'cmd': '', 'percent': 0}
#     for c, v in config.VA_CMD_LIST.items():
#         for x in v:
#             vrt = fuzz.ratio(cmd, x)
#             if vrt > rc['percent']:
#                 rc['cmd'] = c
#                 rc['percent'] = vrt
#     return rc

# def execute_cmd(cmd: str, voice: str):
    
#     if cmd == 'help':
#         text = "Я вмію розказувати жарти, відкривати браузери, працювати офлайн, і багато чого іншого"
#         tts.va_speak(text)
#     elif cmd == 'open_browser':
#         play("ok")
#         webbrowser.open("https://www.browser.com")
#     elif cmd == 'open_youtube':
#         play("ok")
#         webbrowser.open("https://www.youtube.com")
#     elif cmd == 'open_google':
#         play("ok")
#         webbrowser.open("https://www.google.com")
#     elif cmd == 'music':
#         subprocess.Popen([f'{CDIR}\\custom-commands\\Run music.exe'])
#         play("ok")
#     elif cmd == 'sound_off':
#         play("ok", True)
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
#         volume.SetMute(1, None)
#     elif cmd == 'sound_on':
#         devices = AudioUtilities.GetSpeakers()
#         interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#         volume = cast(interface, POINTER(IAudioEndpointVolume))
#         volume.SetMute(0, None)
#         play("ok")
#     elif cmd == 'off':
#         play("off", True)
#         porcupine.delete()
#         exit(0)

# # Recorder setup and listening loop
# recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
# recorder.start()
# print('Using device: %s' % recorder.selected_device)

# print(f"Jarvis (v3.0) начал свою работу ...")
# play("run")
# time.sleep(0.5)

# ltc = time.time() - 1000

# while True:
#     try:
#         pcm = recorder.read()
#         keyword_index = porcupine.process(pcm)

#         if keyword_index >= 0:
#             recorder.stop()
#             play("greet", True)
#             print("Yes, sir.")
#             recorder.start()  # Prevent self-recording
#             ltc = time.time()

#         while time.time() - ltc <= 10:
#             pcm = recorder.read()
#             sp = struct.pack("h" * len(pcm), *pcm)

#             if kaldi_rec.AcceptWaveform(sp):
#                 if va_respond(json.loads(kaldi_rec.Result())["text"]):
#                     ltc = time.time()

#                 break

#     except Exception as err:
#         print(f"Unexpected {err=}, {type(err)=}")
#         raise































# import os
# import random
# import webbrowser
# import pvporcupine
# import simpleaudio as sa
# from pvrecorder import PvRecorder
# from rich import print
# import vosk
# import sys
# import queue
# import json
# import struct
# import config
# from fuzzywuzzy import fuzz
# import tts
# import datetime
# from num2words import num2words
# import subprocess
# import time
# import threading

# # Import the animation classes
# from classes import MovingMan, VoiceAssistant

# # Initialize the animation system
# animation_root = tk.Tk()
# animation_control = MovingMan(animation_root)

# # Initialize voice assistant with animation control
# assistant = VoiceAssistant(animation_control)

# # The rest of the provided code here...

# # Adjust the function to include animation control
# def execute_cmd(cmd: str, voice: str):
#     if cmd == 'open_browser':
#         play("ok")
#         animation_control.switch_animation("jump")  # Start jump animation
#         webbrowser.open("https://www.browser.com")
#         animation_control.switch_animation("standart")  # Return to standard animation
#     elif cmd == 'open_youtube':
#         play("ok")
#         animation_control.switch_animation("jump")
#         webbrowser.open("https://www.youtube.com")
#         animation_control.switch_animation("standart")
#     elif cmd == 'open_google':
#         play("ok")
#         animation.animation_start()
#         webbrowser.open("https://www.google.com")
#         animation.animation_end()

    # elif cmd == 'music':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Run music.exe'])
    #     play("ok")

    # elif cmd == 'music_off':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Stop music.exe'])
    #     time.sleep(0.2)
    #     play("ok")

    # elif cmd == 'music_save':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Save music.exe'])
    #     time.sleep(0.2)
    #     play("ok")

    # elif cmd == 'music_next':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Next music.exe'])
    #     time.sleep(0.2)
    #     play("ok")

    # elif cmd == 'music_prev':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Prev music.exe'])
    #     time.sleep(0.2)
    #     play("ok")

    # elif cmd == 'sound_off':
    #     play("ok", True)

    #     devices = AudioUtilities.GetSpeakers()
    #     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #     volume = cast(interface, POINTER(IAudioEndpointVolume))
    #     volume.SetMute(1, None)

    # elif cmd == 'sound_on':
    #     devices = AudioUtilities.GetSpeakers()
    #     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #     volume = cast(interface, POINTER(IAudioEndpointVolume))
    #     volume.SetMute(0, None)

    #     play("ok")

    # elif cmd == 'thanks':
    #     play("thanks")

    # elif cmd == 'stupid':
    #     play("stupid")

    # elif cmd == 'gaming_mode_on':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to gaming mode.exe'])
    #     play("ready")

    # elif cmd == 'gaming_mode_off':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch back to workspace.exe'])
    #     play("ready")

    # elif cmd == 'switch_to_headphones':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to headphones.exe'])
    #     time.sleep(0.5)
    #     play("ready")

    # elif cmd == 'switch_to_dynamics':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to dynamics.exe'])
    #     time.sleep(0.5)
    #     play("ready")
    # elif cmd == 'off':
    #     animation_control.close_window()
    #     porcupine.delete()
    #     exit(0)
        
