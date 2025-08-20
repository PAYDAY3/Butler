import tkinter as tk
from tkinter import scrolledtext
import sys
import os

class CommandPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.command_callback = None
        self.config(bg='white')

        # Input Frame
        self.input_frame = tk.Frame(self, bg='white')
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.input_entry = tk.Entry(self.input_frame, bg='white', fg='black')
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.send_text_command)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_text_command)
        self.send_button.pack(side=tk.LEFT, padx=(5, 0))

        self.listen_button = tk.Button(self.input_frame, text="Listen", command=self.send_listen_command)
        self.listen_button.pack(side=tk.LEFT, padx=(5, 0))

        self.clear_button = tk.Button(self.input_frame, text="Clear", command=self.clear_history)
        self.clear_button.pack(side=tk.LEFT, padx=(5, 0))

        self.restart_button = tk.Button(self.input_frame, text="Restart", command=self.restart_application)
        self.restart_button.pack(side=tk.LEFT, padx=(5, 0))

        # Output Frame
        self.output_frame = tk.Frame(self, bg='white')
        self.output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, bg='white', fg='black', state='disabled')
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def set_command_callback(self, callback):
        self.command_callback = callback

    def send_text_command(self, event=None):
        command = self.input_entry.get().strip()
        if command and self.command_callback:
            self.command_callback("text", command)
            self.input_entry.delete(0, tk.END)

    def send_listen_command(self):
        if self.command_callback:
            self.command_callback("voice", None)

    def clear_history(self):
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')

    def restart_application(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def append_to_history(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
