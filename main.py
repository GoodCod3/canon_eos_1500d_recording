import tkinter as tk
import subprocess
import threading
import queue
import signal
import numpy as np
from PIL import Image, ImageTk


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Recording audio and video")

        self.video_label = tk.Label(root)
        self.video_label.pack(pady=20)

        self.start_button = tk.Button(root, text="Start recording", command=self.start_recording)
        self.start_button.pack(pady=20)

        self.cancel_button = tk.Button(root, text="Stop recording", command=self.cancel_recording)
        self.cancel_button.pack(pady=20)

        self.output_text = tk.Text(root, height=10, width=50)
        self.output_text.pack(pady=20)

        self.process = None  
        self.queue = queue.Queue()  

        self.video_thread = threading.Thread(target=self.show_video)
        self.video_thread.daemon = True
        self.video_thread.start()

    def show_video(self):
        command = ["gphoto2", "--stdout", "--capture-movie"]
        ffmpeg_command = [
            "ffmpeg", "-f", "mjpeg", "-i", "pipe:0", "-pix_fmt", "bgr24",
            "-vf", "scale=640:480", "-f", "rawvideo", "pipe:1"
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=process.stdout, stdout=subprocess.PIPE)

        while True:
            raw_frame = ffmpeg_process.stdout.read(640 * 480 * 3)
            if not raw_frame:
                break

            if len(raw_frame) == 640 * 480 * 3:
                frame = np.frombuffer(raw_frame, np.uint8).reshape((480, 640, 3))

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

        process.stdout.close()
        process.stderr.close()
        ffmpeg_process.stdout.close()
        ffmpeg_process.stderr.close()

    def start_recording(self):
        if not self.process:  
            self.thread = threading.Thread(target=self.run_script)
            self.thread.start()

    def run_script(self):
        self.output_text.insert(tk.END, "Executing Bash script...\n") 
        self.process = subprocess.Popen(
            ['bash', 'recording.sh'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            bufsize=1  
        )

        for line in iter(self.process.stdout.readline, ''):
            self.output_text.insert(tk.END, line)
            self.queue.put(line)  

        for line in iter(self.process.stderr.readline, ''):
            self.output_text.insert(tk.END, line)
            self.queue.put(line)

        self.process.stdout.close()  
        self.process.stderr.close()  
        self.process.wait()  
        self.queue.put("Recording finished.\n")  
        self.process = None  

    def process_output(self):
        while True:
            try:
                line = self.queue.get(timeout=1)  
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
            except queue.Empty:
                if self.process is None:
                    break  

    def cancel_recording(self):
        if self.process:
            self.process.send_signal(signal.SIGINT)  
            self.process = None  
            self.output_text.insert(tk.END, "Recording cancelled.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
