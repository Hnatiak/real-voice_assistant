import pymongo
from pymongo import MongoClient
from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import io
from utils import play
import config

# from main import play

client = MongoClient(config.MONGODB_URL)
db = client["user_database"]
collection = db["users"]

# Дефолтні статуси
DEFAULT_STATUSES = ["user", "admin", "doctor", "darling", "parents"]

def upload_photo():
    filepath = filedialog.askopenfilename(
        title="Виберіть фото",
        filetypes=[("Image Files", "*.*")]
    )
    if filepath:
        return filepath
    else:
        return None

# Функція для збереження фото у бінарному вигляді
def save_photo_as_binary(filepath):
    try:
        with open(filepath, "rb") as file:
            binary_data = file.read()
        return binary_data
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося зчитати файл: {e}")
        return None

# Функція для фотографування за допомогою камери
def capture_photo():
    # camera = cv2.VideoCapture(0)
    # if not camera.isOpened():
    #     messagebox.showerror("Помилка", "Не вдалося відкрити камеру!")
    #     return None
    
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        play("error")
        print("Камера не відкривається. Перевірте налаштування або доступність пристрою.")
        return None
    
    captured_image = None
    while True:
        ret, frame = camera.read()
        if not ret:
            play("error")
            messagebox.showerror("Помилка", "Не вдалося отримати зображення з камери!")
            break

        cv2.imshow("Зніміть фото", frame)

        key = cv2.waitKey(1)
        if key == ord('c'):
            captured_image = frame
            break
        elif key == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

    if captured_image is not None:
        return captured_image
    return None

def save_user_data(data):
    try:
        existing_user = collection.find_one({"first_name": data["first_name"], "last_name": data["last_name"]})
        if existing_user:
            messagebox.showerror("Помилка", "Користувач з таким ім'ям і прізвищем вже існує!")
            return False

        # Додавання даних у MongoDB
        collection.insert_one(data)
        play("new_user_success")
        messagebox.showinfo("Успіх", "Користувач успішно зареєстрований!")
        return True
    except Exception as e:
        play("new_user_error")
        messagebox.showerror("Помилка", f"Не вдалося зберегти дані: {e}")
        return False

# Головна функція для реєстрації
def register_new_user():
    # Вікно реєстрації
    root = tk.Tk()
    root.title("Реєстрація користувача")
    root.geometry("400x600")
    
    # Поля для введення даних
    tk.Label(root, text="Ім'я:").pack()
    first_name_entry = tk.Entry(root)
    first_name_entry.pack()

    tk.Label(root, text="Прізвище:").pack()
    last_name_entry = tk.Entry(root)
    last_name_entry.pack()

    tk.Label(root, text="По-батькові (Не обов'язково):").pack()
    middle_name_entry = tk.Entry(root)
    middle_name_entry.pack()

    tk.Label(root, text="Дата народження (YYYY-MM-DD):").pack()
    dob_entry = tk.Entry(root)
    dob_entry.pack()

    tk.Label(root, text="Стан одруження:").pack()
    marital_status_entry = tk.Entry(root)
    marital_status_entry.pack()

    tk.Label(root, text="Статус (user, admin, doctor, darling, parents):").pack()
    status_entry = tk.Entry(root)
    status_entry.insert(0, "user")
    status_entry.pack()

    # Фотографія
    photo_label = tk.Label(root, text="Фото: (не вибрано)")
    photo_label.pack()

    captured_photo = None  # Змінна для збереження фото

    def select_photo_from_pc():
        filepath = upload_photo()
        if filepath:
            photo_label.config(text=f"Фото: {os.path.basename(filepath)}")
            photo_label.filepath = filepath

    def take_photo_with_camera():
        nonlocal captured_photo
        photo_button_camera["state"] = "disabled"
        captured_photo_temp = capture_photo()
        if captured_photo_temp is not None:
            # Показати фото користувачу
            cv2.imshow("Підтвердження фото", captured_photo_temp)
            key = cv2.waitKey(0)
            cv2.destroyAllWindows()
            if key == ord('y'):  # Підтвердити фото
                captured_photo = cv2.imencode('.jpg', captured_photo_temp)[1].tobytes()
                photo_label.config(text="Фото зроблено!")
            else:
                captured_photo = None
                photo_button_camera["state"] = "normal"  # Дозволити повторно зробити фото

    photo_button_pc = tk.Button(root, text="Завантажити фото з ПК", command=select_photo_from_pc)
    photo_button_pc.pack()

    photo_button_camera = tk.Button(root, text="Зробити фото камерою", command=take_photo_with_camera)
    photo_button_camera.pack()

    # Функція для збереження
    def submit():
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        middle_name = middle_name_entry.get().strip()
        dob = dob_entry.get().strip()
        marital_status = marital_status_entry.get().strip()
        status = status_entry.get().strip()

        if not first_name or not last_name or not dob or not marital_status or not status:
            messagebox.showerror("Помилка", "Усі поля повинні бути заповнені!")
            return

        try:
            dob = datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Помилка", "Дата народження повинна бути у форматі YYYY-MM-DD!")
            return

        if status not in DEFAULT_STATUSES:
            messagebox.showerror("Помилка", f"Статус повинен бути одним із: {', '.join(DEFAULT_STATUSES)}")
            return

        photo_binary = None
        if captured_photo:
            photo_binary = captured_photo
        elif hasattr(photo_label, 'filepath'):
            photo_binary = save_photo_as_binary(photo_label.filepath)
            if not photo_binary:
                return

        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "middle_name": middle_name,
            "date_of_birth": dob.strftime("%Y-%m-%d"),
            "marital_status": marital_status,
            "status": status,
            "photo": photo_binary,
        }

        if save_user_data(user_data):
            root.destroy()

    submit_button = tk.Button(root, text="Зареєструвати", command=submit)
    submit_button.pack()

    root.mainloop()









# import pymongo
# from pymongo import MongoClient
# from datetime import datetime
# import os
# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# from PIL import Image, ImageTk
# import cv2
# import io

# client = MongoClient("mongodb+srv://jhewgnva34:MEtqFXoZ9H9xJjYF@cluster0.9ygmg.mongodb.net/")
# db = client["user_database"]
# collection = db["users"]

# DEFAULT_STATUSES = ["user", "admin", "doctor", "darling", "parents"]

# def upload_photo():
#     filepath = filedialog.askopenfilename(
#         title="Виберіть фото",
#         filetypes=[("Image Files", "*.*")]
#     )
#     if filepath:
#         return filepath
#     else:
#         return None

# def save_photo_as_binary(filepath):
#     try:
#         with open(filepath, "rb") as file:
#             binary_data = file.read()
#         return binary_data
#     except Exception as e:
#         messagebox.showerror("Помилка", f"Не вдалося зчитати файл: {e}")
#         return None

# def capture_photo():
#     camera = cv2.VideoCapture(0)
#     if not camera.isOpened():
#         messagebox.showerror("Помилка", "Не вдалося відкрити камеру!")
#         return None

#     captured_image = None
#     while True:
#         ret, frame = camera.read()
#         if not ret:
#             messagebox.showerror("Помилка", "Не вдалося отримати зображення з камери!")
#             break

#         cv2.imshow("Зніміть фото", frame)

#         key = cv2.waitKey(1)
#         if key == ord('c'):
#             captured_image = frame
#             break
#         elif key == ord('q'):
#             break

#     camera.release()
#     cv2.destroyAllWindows()

#     if captured_image is not None:
#         return captured_image
#     return None

# def save_user_data(data):
#     try:
#         existing_user = collection.find_one({"first_name": data["first_name"], "last_name": data["last_name"]})
#         if existing_user:
#             messagebox.showerror("Помилка", "Користувач з таким ім'ям і прізвищем вже існує!")
#             return False

#         collection.insert_one(data)
#         messagebox.showinfo("Успіх", "Користувач успішно зареєстрований!")
#         return True
#     except Exception as e:
#         messagebox.showerror("Помилка", f"Не вдалося зберегти дані: {e}")
#         return False

# def register_new_user():
#     def create_window():
#         # Створення GUI елементів
#         root = tk.Tk()
#         root.title("Реєстрація користувача")
#         root.geometry("500x650")
#         root.configure(bg="#f0f0f0")
        
#         # Ваш код для GUI
#         style = ttk.Style()
#         style.configure("TButton",
#                         background="#4CAF50",
#                         foreground="white",
#                         font=("Helvetica", 12),
#                         padding=10)
#         style.configure("TLabel",
#                         font=("Helvetica", 12),
#                         background="#f0f0f0")
#         style.configure("TEntry",
#                         font=("Helvetica", 12),
#                         padding=5)

#         # Поля для введення даних
#         tk.Label(root, text="Ім'я:", bg="#f0f0f0").pack(pady=5)
#         first_name_entry = ttk.Entry(root)
#         first_name_entry.pack(pady=5, fill="x", padx=20)

#         tk.Label(root, text="Прізвище:", bg="#f0f0f0").pack(pady=5)
#         last_name_entry = ttk.Entry(root)
#         last_name_entry.pack(pady=5, fill="x", padx=20)

#         tk.Label(root, text="По-батькові (Не обов'язково):", bg="#f0f0f0").pack(pady=5)
#         middle_name_entry = ttk.Entry(root)
#         middle_name_entry.pack(pady=5, fill="x", padx=20)

#         tk.Label(root, text="Дата народження (YYYY-MM-DD):", bg="#f0f0f0").pack(pady=5)
#         dob_entry = ttk.Entry(root)
#         dob_entry.pack(pady=5, fill="x", padx=20)

#         tk.Label(root, text="Стан одруження:", bg="#f0f0f0").pack(pady=5)
#         marital_status_entry = ttk.Entry(root)
#         marital_status_entry.pack(pady=5, fill="x", padx=20)

#         tk.Label(root, text="Статус (user, admin, doctor, darling, parents):", bg="#f0f0f0").pack(pady=5)
#         status_entry = ttk.Entry(root)
#         status_entry.insert(0, "user")
#         status_entry.pack(pady=5, fill="x", padx=20)

#         # Фотографія
#         photo_label = tk.Label(root, text="Фото: (не вибрано)", bg="#f0f0f0")
#         photo_label.pack(pady=10)
        
#         root.mainloop()

#     captured_photo = None

#     def select_photo_from_pc():
#         filepath = upload_photo()
#         if filepath:
#             photo_label.config(text=f"Фото: {os.path.basename(filepath)}")
#             photo_label.filepath = filepath

#     def take_photo_with_camera():
#         nonlocal captured_photo
#         photo_button_camera["state"] = "disabled"
#         captured_photo_temp = capture_photo()
#         if captured_photo_temp is not None:
#             # Показати фото користувачу
#             cv2.imshow("Підтвердження фото", captured_photo_temp)
#             key = cv2.waitKey(0)
#             cv2.destroyAllWindows()
#             if key == ord('y'):  # Підтвердити фото
#                 captured_photo = cv2.imencode('.jpg', captured_photo_temp)[1].tobytes()
#                 photo_label.config(text="Фото зроблено!")
#             else:
#                 captured_photo = None
#                 photo_button_camera["state"] = "normal"  # Дозволити повторно зробити фото

#     photo_button_pc = ttk.Button(root, text="Завантажити фото з ПК", command=select_photo_from_pc)
#     photo_button_pc.pack(pady=10)

#     photo_button_camera = ttk.Button(root, text="Зробити фото камерою", command=take_photo_with_camera)
#     photo_button_camera.pack(pady=10)

#     # Функція для збереження
#     def submit():
#         first_name = first_name_entry.get().strip()
#         last_name = last_name_entry.get().strip()
#         middle_name = middle_name_entry.get().strip()
#         dob = dob_entry.get().strip()
#         marital_status = marital_status_entry.get().strip()
#         status = status_entry.get().strip()

#         if not first_name or not last_name or not dob or not marital_status or not status:
#             messagebox.showerror("Помилка", "Усі поля повинні бути заповнені!")
#             return

#         try:
#             dob = datetime.strptime(dob, "%Y-%m-%d")
#         except ValueError:
#             messagebox.showerror("Помилка", "Дата народження повинна бути у форматі YYYY-MM-DD!")
#             return

#         if status not in DEFAULT_STATUSES:
#             messagebox.showerror("Помилка", f"Статус повинен бути одним із: {', '.join(DEFAULT_STATUSES)}")
#             return

#         photo_binary = None
#         if captured_photo:
#             photo_binary = captured_photo
#         elif hasattr(photo_label, 'filepath'):
#             photo_binary = save_photo_as_binary(photo_label.filepath)
#             if not photo_binary:
#                 return

#         user_data = {
#             "first_name": first_name,
#             "last_name": last_name,
#             "middle_name": middle_name,
#             "date_of_birth": dob.strftime("%Y-%m-%d"),
#             "marital_status": marital_status,
#             "status": status,
#             "photo": photo_binary,
#         }

#         if save_user_data(user_data):
#             root.destroy()

#     submit_button = ttk.Button(root, text="Зареєструвати", command=submit)
#     submit_button.pack(pady=20)

#     root.mainloop()