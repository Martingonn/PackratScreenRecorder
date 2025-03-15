import pyaudio
import wave
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
import cv2
import numpy as np
import pyautogui
import datetime

# Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono for compatibility
RATE = 44100
CHUNK = 1024
DEFAULT_OUTPUT_FILENAME_AUDIO = "output_audio.wav"
DEFAULT_OUTPUT_FILENAME_VIDEO = "output_video.mp4"

class Recorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen and Audio Recorder")
        self.recording = False
        self.audio = None
        self.stream = None
        self.frames_audio = []
        self.frames_video = []
        self.output_filename_audio = DEFAULT_OUTPUT_FILENAME_AUDIO
        self.output_filename_video = DEFAULT_OUTPUT_FILENAME_VIDEO
        
        # GUI components
        self.label = tk.Label(self.root, text="Press Record to start")
        self.label.pack()
        
        self.record_button = tk.Button(self.root, text="Record", command=self.start_recording)
        self.record_button.pack()
        
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack()
        
        self.save_button = tk.Button(self.root, text="Save", command=self.save_recording, state=tk.DISABLED)
        self.save_button.pack()
        
        # Save path entries
        self.save_path_label_audio = tk.Label(self.root, text="Save Audio Path:")
        self.save_path_label_audio.pack()
        
        self.save_path_entry_audio = tk.Entry(self.root, width=50)
        self.save_path_entry_audio.insert(0, DEFAULT_OUTPUT_FILENAME_AUDIO)
        self.save_path_entry_audio.pack()
        
        self.browse_button_audio = tk.Button(self.root, text="Browse Audio", command=self.browse_save_path_audio)
        self.browse_button_audio.pack()
        
        self.save_path_label_video = tk.Label(self.root, text="Save Video Path:")
        self.save_path_label_video.pack()
        
        self.save_path_entry_video = tk.Entry(self.root, width=50)
        self.save_path_entry_video.insert(0, DEFAULT_OUTPUT_FILENAME_VIDEO)
        self.save_path_entry_video.pack()
        
        self.browse_button_video = tk.Button(self.root, text="Browse Video", command=self.browse_save_path_video)
        self.browse_button_video.pack()
        
    def start_recording(self):
        self.recording = True
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        
        # Create PyAudio object
        self.audio = pyaudio.PyAudio()
        
        try:
            # Open stream
            self.stream = self.audio.open(format=FORMAT,
                                          channels=CHANNELS,
                                          rate=RATE,
                                          input=True,
                                          frames_per_buffer=CHUNK)
        except OSError as e:
            messagebox.showerror("Error", f"Failed to open stream: {e}")
            self.stop_recording()
            return
        
        self.frames_audio = []
        self.frames_video = []
        
        # Start recording in separate threads
        self.thread_audio = Thread(target=self.record_audio)
        self.thread_video = Thread(target=self.record_video)
        self.thread_audio.start()
        self.thread_video.start()
        
    def record_audio(self):
        while self.recording:
            try:
                data = self.stream.read(CHUNK)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading from stream: {e}")
                self.stop_recording()
                return
            self.frames_audio.append(data)
        
    def record_video(self):
        # Video recording parameters
        size = (pyautogui.size()[0], pyautogui.size()[1])
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = 12.0
        
        out = cv2.VideoWriter("temp.mp4", fourcc, fps, size)
        
        while self.recording:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
        
        out.release()
        
    def stop_recording(self):
        self.recording = False
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        
        if self.stream is not None:
            # Close and terminate everything properly
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
        
        self.label.config(text="Recording stopped. Press Save to save the files.")
        
    def save_recording(self):
        try:
            # Save the recorded audio as a .wav file
            self.output_filename_audio = self.save_path_entry_audio.get()
            if not self.output_filename_audio.endswith('.wav'):
                self.output_filename_audio += '.wav'
            
            waveFile = wave.open(self.output_filename_audio, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(self.frames_audio))
            waveFile.close()
            
            # Save the recorded video
            self.output_filename_video = self.save_path_entry_video.get()
            if not self.output_filename_video.endswith('.mp4'):
                self.output_filename_video += '.mp4'
            
            import shutil
            shutil.move("temp.mp4", self.output_filename_video)
            
            self.label.config(text="Recordings saved successfully.")
            self.save_button.config(state=tk.DISABLED)
            messagebox.showinfo("Success", f"Audio saved to {self.output_filename_audio} and Video saved to {self.output_filename_video}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def browse_save_path_audio(self):
        path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if path:
            self.save_path_entry_audio.delete(0, tk.END)
            self.save_path_entry_audio.insert(0, path)
            
    def browse_save_path_video(self):
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if path:
            self.save_path_entry_video.delete(0, tk.END)
            self.save_path_entry_video.insert(0, path)
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Recorder()
    app.run()
