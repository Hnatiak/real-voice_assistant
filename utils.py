import simpleaudio as sa
import os

CDIR = os.getcwd()

def play(phrase, wait_done=True):
    # global recorder
    filename = f"{CDIR}\\sound\\"

    if phrase == "greet":  # for py 3.8
        filename += "greet.wav"
    elif phrase == "ok":
        filename += "accept.wav"  # f"ok{random.choice([1, 2, 3])}.wav"
    elif phrase == "not_found":
        filename += "dont_understand.wav"
    elif phrase == "thanks":
        filename += "thx.wav"
    elif phrase == "run":
        filename += "welcome.wav"
    elif phrase == "stupid":
        filename += "stupid.wav"
    elif phrase == "ready":
        filename += "ready.wav"
    elif phrase == "off":
        filename += "bye.wav"
    elif phrase == "im_doing":
        filename += "im_doing.wav"
    elif phrase == "goingtodo":
        filename += "goingtodo.wav"
    elif phrase == "register-start":
        filename += "new_user_register_attention.wav"
    elif phrase == "new_user_success":
        filename += "new_user_success.wav"
    elif phrase == "new_user_error":
        filename += "new_user_error.wav"
    elif phrase == "error":
        filename += "error.wav"
    elif phrase == "error_operation":
        filename += "error_operation.wav"
    elif phrase == "error_command":
        filename += "error_command.wav"

    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()

    if wait_done:
        play_obj.wait_done()
        time.sleep(0.5)
        
#     if wait_done:
#         recorder.stop()

#     wave_obj = sa.WaveObject.from_wave_file(filename)
#     play_obj = wave_obj.play()

#     if wait_done:
#         play_obj.wait_done()
#         # time.sleep((len(wave_obj.audio_data) / wave_obj.sample_rate) + 0.5)
#         # print("END")
#         # time.sleep(0.5)
#         recorder.start()