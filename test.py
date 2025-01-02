# import pyttsx3

# # Ініціалізація pyttsx3
# engine = pyttsx3.init()

# # Отримуємо всі доступні голоси
# voices = engine.getProperty('voices')

# # Вибираємо голос, що підтримує українську мову (зазвичай він доступний на Windows, якщо встановлено українську мову в системі)
# for voice in voices:
#     if "ukrainian" in voice.languages:
#         engine.setProperty('voice', voice.id)
#         break

# # Встановлюємо швидкість голосу (за бажанням)
# engine.setProperty('rate', 150)

# # Встановлюємо текст для озвучування
# text = "Привіт, як я можу допомогти?"

# # Озвучуємо текст
# engine.say(text)

# # Чекаємо завершення озвучення
# engine.runAndWait()




# from gtts import gTTS
# import os

# # Текст для озвучення
# text = "Привіт, як я можу допомогти?"

# # Створюємо об'єкт для озвучення
# tts = gTTS(text, lang='uk')

# # Зберігаємо аудіо в файл
# audio_file = "output.mp3"
# tts.save(audio_file)

# # Відтворюємо файл (якщо ви хочете прослухати)
# os.system(f"start {audio_file}")





# from pydub import AudioSegment

# def convert_to_ms(time_str):
#     """
#     Перетворює час у форматі HH:MM:SS в мілісекунди.
#     """
#     try:
#         # Переводимо час з формату HH:MM:SS в мілісекунди
#         hours, minutes, seconds = map(int, time_str.split(':'))
#         return (hours * 3600 + minutes * 60 + seconds) * 1000
#     except ValueError:
#         raise ValueError(f"Невірний формат часу: {time_str}. Час має бути у форматі HH:MM:SS.")

# def cut_audio(file_path, intervals):
#     try:
#         audio = AudioSegment.from_file(file_path)
#     except Exception as e:
#         print(f"Помилка при завантаженні аудіофайлу: {e}")
#         return
    
#     for start, end, name in intervals:
#         try:
#             start_ms = convert_to_ms(start)
#             end_ms = convert_to_ms(end)
#         except ValueError as e:
#             print(e)
#             continue
        
#         # Перевіряємо чи є інтервал в межах доступного аудіо
#         if start_ms < 0 or end_ms > len(audio):
#             print(f"Інтервал з {start} до {end} виходить за межі аудіофайлу.")
#             continue
        
#         # Обрізаємо аудіо
#         segment = audio[start_ms:end_ms]
        
#         # Зберігаємо обрізане аудіо
#         output_name = f"audios/{name}.wav"
#         segment.export(output_name, format="wav")
#         print(f"Успішно обрізано аудіо з {start} до {end}, з іменем: {output_name}")
        
#     print("Усі обрізані частини успішно збережено!")

# # Приклад використання
# intervals = [
#     ('00:00:00', '00:00:02', 'welcome'),
#     ('00:00:03', '00:00:06', 'dontunderstand')
# ]

# # Вкажіть шлях до вашого аудіофайлу
# file_path = "audio.wav"

# cut_audio(file_path, intervals)






# from pydub import AudioSegment

# def convert_to_ms(time_str):
#     """
#     Перетворює час у форматі HH:MM:SS:SSS в мілісекунди.
#     """
#     try:
#         # Переводимо час з формату HH:MM:SS:SSS в мілісекунди
#         hours, minutes, seconds, milliseconds = map(int, time_str.split(':'))
        
#         # Повертаємо час в мілісекунди
#         total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
#         return total_ms
#     except ValueError:
#         raise ValueError(f"Невірний формат часу: {time_str}. Час має бути у форматі HH:MM:SS:SSS.")

# def cut_audio(file_path, intervals):
#     try:
#         audio = AudioSegment.from_file(file_path)
#     except Exception as e:
#         print(f"Помилка при завантаженні аудіофайлу: {e}")
#         return
    
#     for start, end, name in intervals:
#         try:
#             start_ms = convert_to_ms(start)
#             end_ms = convert_to_ms(end)
#         except ValueError as e:
#             print(e)
#             continue
        
#         # Перевіряємо чи є інтервал в межах доступного аудіо
#         if start_ms < 0 or end_ms > len(audio):
#             print(f"Інтервал з {start} до {end} виходить за межі аудіофайлу.")
#             continue
        
#         # Обрізаємо аудіо
#         segment = audio[start_ms:end_ms]
        
#         # Зберігаємо обрізане аудіо
#         output_name = f"audios/{name}.wav"
#         segment.export(output_name, format="wav")
#         print(f"Успішно обрізано аудіо з {start} до {end}, з іменем: {output_name}")
        
#     print("Усі обрізані частини успішно збережено!")

# # Приклад використання
# intervals = [
#     ('00:00:03:400', '00:00:09:400', 'new_user_inputs'),  # ГОТОВО
#     ('00:00:09:700', '00:00:11:800', 'accept'), # ГОТОВО
#     ('00:00:11:900', '00:00:13:200', 'bye'), # ГОТОВО
#     ('00:00:13:500', '00:00:14:800', 'im_doing'), # ГОТОВО
#     ('00:00:14:900', '00:00:18:300', 'dont_understand'), # ГОТОВО
#     ('00:00:18:500', '00:00:21:900', 'dont_understand_2'), # ГОТОВО
#     ('00:00:22:200', '00:00:28:200', 'new_user_success'), # ГОТОВО
#     ('00:00:28:300', '00:00:36:000', 'new_user_error'), # ГОТОВО
#     ('00:00:36:400', '00:00:39:800', 'error_command'), # ГОТОВО
#     ('00:00:39:900', '00:00:43:500', 'error_operation'), # ГОТОВО
#     ('00:00:43:800', '00:00:45:800', 'im_preparing_todo'), # ГОТОВО
#     ('00:00:46:000', '00:00:47:400', 'yes_sir'), # ГОТОВО
#     ('00:00:47:600', '00:00:50:800', 'welcome'), # ГОТОВО
#     ('00:00:51:000', '00:00:56:100', 'internet_error'), # ГОТОВО
    
#     ('00:01:01:000', '00:01:06:600', 'im_ready'), # ГОТОВО
#     ('00:01:08:000', '00:01:11:900', 'thx_bye'), # ГОТОВО
#     ('00:01:12:100', '00:01:13:600', 'try_again'), # ГОТОВО
#     ('00:01:13:800', '00:01:15:400', 'ur_welc'), # ГОТОВО
# ]

# # Вкажіть шлях до вашого аудіофайлу
# file_path = "qwe.wav"

# cut_audio(file_path, intervals)










# import os
# import subprocess

# def disable_wifi():
#     # Отримуємо список інтерфейсів через subprocess з кодуванням UTF-8
#     result = subprocess.run('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    
#     # Перевіряємо, чи успішно виконалася команда
#     if result.returncode != 0:
#         print(f"Помилка виконання команди: {result.stderr}")
#         return

#     interfaces = result.stdout

#     # Список можливих назв інтерфейсів для Wi-Fi
#     possible_interfaces = ["Wi-Fi", "Беспроводная сеть", "Wireless Network", "WLAN", "Wi-Fi Direct"]
    
#     # Шукаємо перший знайдений інтерфейс
#     for interface in possible_interfaces:
#         if interface in interfaces:
#             print(f"Інтерфейс знайдений: {interface}")
#             os.system(f'netsh interface set interface "{interface}" disabled')
#             print(f"Wi-Fi інтерфейс '{interface}' вимкнено.")
#             return

#     print("Wi-Fi інтерфейс не знайдений.")
    
# # Викликаємо функцію для вимкнення Wi-Fi
# disable_wifi()










from pynput.keyboard import Controller, Key
import time

def write_text():
    keyboard = Controller()

    time.sleep(2)  # Даємо час для активації потрібного вікна

    # Текст для введення
    text = "Hello, World! This is an example text with special chars: @#$%^&*()"

    # Вводимо текст з паузами
    for char in text:
        keyboard.type(char)
        time.sleep(0.1)  # Невелика пауза між символами

    # Натискання клавіші Enter
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

write_text()
















# from PIL import Image
# import io
# from pymongo import MongoClient

# # Підключення до MongoDB
# client = MongoClient("mongodb+srv://jhewgnva34:MEtqFXoZ9H9xJjYF@cluster0.9ygmg.mongodb.net/")
# db = client["user_database"]
# collection = db["users"]

# # Завантаження фото користувача за ID
# def view_user_photo(user_id):
#     user = collection.find_one({"_id": user_id})
#     print(user.get("last_name"),
#     user.get("first_name"),
#     user.get("middle_name"),
#     user.get("date_of_birth"),
#     user.get("marital_status"),
#     user.get("status"))
#     if user and user.get("photo"):
#         photo_data = user["photo"]
#         image = Image.open(io.BytesIO(photo_data))
#         image.show()  # Відкриває фото у вікні
#     else:
#         print("Фото не знайдено!")

# # Приклад виклику
# from bson import ObjectId
# view_user_photo(ObjectId("6774296e2d48736f1b2f9084"))