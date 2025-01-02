import tkinter as tk
from PIL import Image, ImageTk
import os
import threading
from queue import Queue
import time

class MovingMan:
    def __init__(self, root, animation_queue):
        self.root = root
        self.animation_queue = animation_queue
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "white")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height, highlightthickness=0, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.animations = {
            "standart": self.load_frames("./resized-images/standart/"),
            "jump": self.load_frames("./resized-images/jump/"),
            "thinking": self.load_frames("./resized-images/thinking/"),
        }

        self.current_frame = 0
        self.current_animation = "standart"
        self.image_on_canvas = self.canvas.create_image(
            screen_width // 2, screen_height // 2,
            image=self.animations[self.current_animation][self.current_frame]
        )
        
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.is_shift_pressed = False

        self.root.bind("<ButtonPress-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)
        self.root.bind("<KeyPress-Shift_L>", self.on_shift_press)
        self.root.bind("<KeyRelease-Shift_L>", self.on_shift_release)



        self.update_animation()
        self.process_animation_queue()

    def load_frames(self, folder):
        frames = []
        file_names = sorted(os.listdir(folder))
        for file_name in file_names:
            if file_name.endswith(".png"):
                frame_path = os.path.join(folder, file_name)
                frame = Image.open(frame_path)
                frames.append(ImageTk.PhotoImage(frame))
        return frames

    def switch_animation(self, animation_name):
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.current_frame = 0

    def update_animation(self):
        frames = self.animations[self.current_animation]
        self.current_frame = (self.current_frame + 1) % len(frames)
        self.canvas.itemconfig(self.image_on_canvas, image=frames[self.current_frame])
        self.root.after(50, self.update_animation)
        
    def start_drag(self, event):
        if self.is_shift_pressed:
            self.is_dragging = True
            self.offset_x = event.x
            self.offset_y = event.y

    def do_drag(self, event):
        if self.is_dragging:
            new_x = self.root.winfo_x() + (event.x - self.offset_x)
            new_y = self.root.winfo_y() + (event.y - self.offset_y)
            self.root.geometry(f"+{new_x}+{new_y}")

    def on_shift_press(self, event):
        self.is_shift_pressed = True

    def on_shift_release(self, event):
        self.is_shift_pressed = False
        self.is_dragging = False

    def process_animation_queue(self):
        def handle_queue():
            last_animation_time = time.time()

            while True:
                if not self.animation_queue.empty():
                    animation_name = self.animation_queue.get()
                    self.switch_animation(animation_name)

                    if animation_name == "thinking":
                        last_animation_time = time.time()
                    else:
                        self.root.after(2000, lambda: self.switch_animation("standart"))

                if self.current_animation == "thinking" and (time.time() - last_animation_time > 12):
                    self.switch_animation("standart")

                time.sleep(0.1)

        threading.Thread(target=handle_queue, daemon=True).start()