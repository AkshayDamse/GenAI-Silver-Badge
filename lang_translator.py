
import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import playsound
import threading
import os
import time

class OneMinuteTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("60-Second Pro Translator")
        self.root.geometry("450x600")
        self.root.configure(bg="#f8f9fa")
        
        self.languages = {
            'English': 'en', 'Hindi': 'hi', 'Spanish': 'es', 
            'French': 'fr', 'German': 'de', 'Japanese': 'ja'
        }
        
        self.recorded_text = ""
        self.translator = Translator()
        self.is_recording = False
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=70)
        header.pack(fill="x")
        tk.Label(header, text="VOICE TRANSLATOR (1 MIN)", font=("Helvetica", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=15)

        # Main Layout
        main_frame = tk.Frame(self.root, bg="#f8f9fa", padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Language Selection
        lang_frame = tk.Frame(main_frame, bg="#f8f9fa")
        lang_frame.pack(fill="x", pady=10)

        self.in_lang = ttk.Combobox(lang_frame, values=list(self.languages.keys()), state="readonly")
        self.in_lang.set("English")
        self.in_lang.grid(row=0, column=0, padx=5)

        tk.Label(lang_frame, text=" ➜ ", bg="#f8f9fa", font=("Arial", 12)).grid(row=0, column=1)

        self.out_lang = ttk.Combobox(lang_frame, values=list(self.languages.keys()), state="readonly")
        self.out_lang.set("Hindi")
        self.out_lang.grid(row=0, column=2, padx=5)

        # Timer Display
        self.timer_label = tk.Label(main_frame, text="01:00", font=("Courier", 24, "bold"), bg="#f8f9fa", fg="#e74c3c")
        self.timer_label.pack(pady=10)

        # Text Output
        self.text_display = tk.Text(main_frame, height=10, width=50, font=("Arial", 10), padx=10, pady=10)
        self.text_display.pack(pady=10)

        # Status
        self.status_var = tk.StringVar(value="Click record to start (60s limit)")
        tk.Label(main_frame, textvariable=self.status_var, bg="#f8f9fa", font=("Arial", 9, "italic")).pack()

        # Control Buttons
        self.record_btn = tk.Button(main_frame, text="🎤 Start 60s Recording", bg="#e74c3c", fg="white", 
                                   font=("Arial", 11, "bold"), width=25, pady=10, command=self.start_recording_thread)
        self.record_btn.pack(pady=10)

        self.trans_btn = tk.Button(main_frame, text="🔊 Translate & Play Audio", bg="#27ae60", fg="white", 
                                  font=("Arial", 11, "bold"), width=25, pady=10, state="disabled", command=self.translate_audio)
        self.trans_btn.pack()

    def update_timer(self):
        count = 60
        while count > 0 and self.is_recording:
            mins, secs = divmod(count, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            count -= 1
        self.timer_label.config(text="01:00")

    def start_recording_thread(self):
        self.is_recording = True
        threading.Thread(target=self.update_timer, daemon=True).start()
        threading.Thread(target=self.record_voice, daemon=True).start()

    def record_voice(self):
        recognizer = sr.Recognizer()
        self.record_btn.config(state="disabled", text="Listening...")
        self.status_var.set("Recording... You have 1 minute.")
        
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                # timeout: wait 15s for speech to start
                # phrase_time_limit: record for up to 60s
                audio = recognizer.listen(source, timeout=15, phrase_time_limit=60)
            
            self.is_recording = False # Stop the timer
            self.status_var.set("Converting speech to text...")
            
            src_code = self.languages[self.in_lang.get()]
            self.recorded_text = recognizer.recognize_google(audio, language=src_code)
            
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, f"YOU SAID:\n{self.recorded_text}\n")
            
            self.trans_btn.config(state="normal")
            self.status_var.set("Captured! Click Translate.")
            
        except Exception as e:
            self.is_recording = False
            self.status_var.set("Error: No speech detected or limit reached.")
            messagebox.showinfo("Timeout", "Recording stopped. Either 60s passed or no speech was heard.")
        
        self.record_btn.config(state="normal", text="🎤 Start 60s Recording")

    def translate_audio(self):
        def process():
            try:
                self.status_var.set("Translating...")
                dest_code = self.languages[self.out_lang.get()]
                src_code = self.languages[self.in_lang.get()]
                
                translated = self.translator.translate(self.recorded_text, src=src_code, dest=dest_code)
                
                self.text_display.insert(tk.END, f"\nTRANSLATION:\n{translated.text}")
                
                tts = gTTS(text=translated.text, lang=dest_code)
                tts.save("temp_out.mp3")
                playsound.playsound("temp_out.mp3")
                os.remove("temp_out.mp3")
                self.status_var.set("Ready")
            except Exception as e:
                messagebox.showerror("Error", f"Translation failed: {e}")
        
        threading.Thread(target=process, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OneMinuteTranslator(root)
    root.mainloop()