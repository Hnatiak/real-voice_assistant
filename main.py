import datetime
import json
import os
import queue
import random
import struct
import subprocess
import sys
import time
from ctypes import POINTER, cast
import openai
import pvporcupine
import simpleaudio as sa
import vosk
import yaml
from comtypes import CLSCTX_ALL
from fuzzywuzzy import fuzz
from pvrecorder import PvRecorder
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)
from rich import print
import webbrowser

import config
import tts

import threading
from queue import Queue
from classes import MovingMan
import tkinter as tk
from register_user import register_new_user
from utils import play
from functions import write_functions


# some consts
CDIR = os.getcwd()
VA_CMD_LIST = yaml.safe_load(
    open('commands.yaml', 'rt', encoding='utf8'),
)

# ChatGPT vars
message_log = [
    {"role": "system", "content": "Ты голосовой ассистент из железного человека."}
]
# Set a flag to keep track of whether this is the first request in the conversation
first_request = True

# init openai
openai.api_key = config.OPENAI_TOKEN

# PORCUPINE
porcupine = pvporcupine.create(
    access_key=config.PICOVOICE_TOKEN,
    keywords=['jarvis'],
    sensitivities=[1]
)
# print(pvporcupine.KEYWORDS)

SEARCH_DIRS = [
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    os.path.expanduser("~\\AppData\\Local"),
    os.path.expanduser("~\\Desktop"),
]

WEB_ALTERNATIVES = {
    "spotify": "https://open.spotify.com/",
    "soundcloud": "https://soundcloud.com/",
    "youtube": "https://www.youtube.com/",
}

# VOSK
model = vosk.Model("model")
samplerate = 16000
device = config.MICROPHONE_INDEX
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()
animation_queue = Queue()

def start_animation():
    root = tk.Tk()
    MovingMan(root, animation_queue)
    root.mainloop()
    
animation_thread = threading.Thread(target=start_animation, daemon=True)
animation_thread.start()


def gpt_answer():
    global message_log

    model_engine = "gpt-3.5-turbo"
    max_tokens = 256  # default 1024
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=message_log,
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=1,
        stop=None
    )

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content


# Функція пошуку програми
def find_program(program_name):
    possible_files = [
        f"{program_name}.exe",
        f"{program_name.lower()}.exe",
        f"{program_name.capitalize()}.exe"
    ]

    for search_dir in SEARCH_DIRS:
        for root, _, files in os.walk(search_dir):
            for file in files:
                if file in possible_files:
                    return os.path.join(root, file)
    return None

# Функція виконання команди
def run_program_or_web(program_keywords):
    for keyword in program_keywords:
        animation_queue.put("thinking")
        print(f"Searching for: {keyword}")
        program_path = find_program(keyword)
        if program_path:
            print(f"Found and running: {program_path}")
            try:
                subprocess.Popen([program_path], shell=True)
                return True
            except Exception as e:
                print(f"Error running {program_path}: {e}")
                return False
    
    print("No program found. Opening Spotify web version.")
    webbrowser.open("https://open.spotify.com/")
    return True


def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def va_respond(voice: str):
    global recorder, message_log, first_request
    print(f"Распознано: {voice}")

    cmd = recognize_cmd(filter_cmd(voice))

    print(cmd)

    if len(cmd['cmd'].strip()) <= 0:
        return False
    elif cmd['percent'] < 70 or cmd['cmd'] not in VA_CMD_LIST.keys():
        # play("not_found")
        # tts.va_speak("Что?")
        if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:

            if first_request:
                message_log.append({"role": "user", "content": voice})
                first_request = False

            # response = gpt_answer()
            message_log.append({"role": "assistant", "content": response})

            recorder.stop()
            tts.va_speak(response)
            time.sleep(0.5)
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
    for c, v in VA_CMD_LIST.items():

        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc

def execute_cmd(cmd: str, voice: str):
    if cmd == 'open_browser':
        animation_queue.put("jump")
        webbrowser.open("https://www.browser.com")
        play("ok")

    elif cmd == 'open_youtube':
        animation_queue.put("jump")
        webbrowser.open("https://www.youtube.com")
        play("ok")

    elif cmd == 'open_google':
        animation_queue.put("jump")
        webbrowser.open("https://www.google.com")
        play("ok")
        
    elif cmd == 'register_new_user':
        play("register-start")
        register_new_user()

    elif cmd == 'music':
        play("goingtodo")
        music_programs = ["Spotify", "SoundCloud", "MusicPlayer"]
        if run_program_or_web(music_programs):
            play("ok")
        else:
            play("not_found")

    elif cmd == 'music_off':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Stop music.exe'])
        time.sleep(0.2)
        play("ok")

    elif cmd == 'music_save':
        subprocess.Popen([f'{CDIR}\\custom-commands\\Save music.exe'])
        time.sleep(0.2)
        play("ok")

    elif cmd == 'music_next':
        animation_queue.put("standart")
        subprocess.Popen([f'{CDIR}\\custom-commands\\Next music.exe'])
        time.sleep(0.2)
        play("ok")

    elif cmd == 'music_prev':
        animation_queue.put("standart")
        subprocess.Popen([f'{CDIR}\\custom-commands\\Prev music.exe'])
        time.sleep(0.2)
        play("ok")

    elif cmd == 'sound_off':
        animation_queue.put("standart")
        play("ok", True)

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)

    elif cmd == 'sound_on':
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0, None)

        play("ok")

    elif cmd == 'thanks':
        animation_queue.put("standart")
        play("thanks")

    elif cmd == 'stupid':
        play("stupid")

    elif cmd == 'gaming_mode_on':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to gaming mode.exe'])
        play("ready")

    elif cmd == 'gaming_mode_off':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch back to workspace.exe'])
        play("ready")

    elif cmd == 'switch_to_headphones':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to headphones.exe'])
        time.sleep(0.5)
        play("ready")

    elif cmd == 'switch_to_dynamics':
        play("ok")
        subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to dynamics.exe'])
        time.sleep(0.5)
        play("ready")
    elif cmd == 'off':
        play("off", True)
        porcupine.delete()
        exit(0)
    elif cmd == 'write_function':
        if any(word in voice for word in ['python', 'пайтон', 'пітон', 'пальтом', 'пальто', 'мальту']):
            play("im_doing")
            write_functions(language="python")
            play("ok")
        elif any(word in voice for word in ['javascript', 'джава скрипт', 'держава скрипт', 'джерела скрипт', 'начала скрипт', 'наживо скрипт', 'навчала скрипт', 'чава скрипки']):
            play("im_doing")
            write_functions(language="javascript")
            play("ok")
        elif any(word in voice for word in ['java', 'джава', 'держава', 'жвава', 'анджело']):
            play("im_doing")
            write_functions(language="java")
            play("ok")
        elif any(word in voice for word in ['с++', 'сі плюс плюс', 'сі', 'плюс плюс']):
            play("im_doing")
            write_functions(language="cpp")
            play("ok")
        else:
            play("not_found")
    


recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
recorder.start()
print('Using device: %s' % recorder.selected_device)

print(f"Jarvis (v3.0) начал свою работу ...")
play("run")
time.sleep(0.5)

ltc = time.time() - 1000

while True:
    try:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            recorder.stop()
            play("greet", True)
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
    
if __name__ == "__main__":
    root = tk.Tk()
    MovingMan(root, queue.Queue())
    root.mainloop()