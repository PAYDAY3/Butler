import tkinter as tk
from tkinter import scrolledtext, ttk
import sys
import os
import json
from package.log_manager import LogManager

logger = LogManager.get_logger(__name__)

class CommandPanel(tk.Frame):
    def __init__(self, master, program_mapping=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.command_callback = None
        self.program_mapping = program_mapping or {}
        self.config(bg='white')

        # --- Configure top-level grid ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Main layout using a PanedWindow (placed in grid) ---
        self.main_paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg='white')
        self.main_paned_window.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # --- Input Frame (at the bottom, placed in grid) ---
        self.input_frame = tk.Frame(self, bg='white')
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1) # Make entry field expandable

        self.input_entry = tk.Entry(self.input_frame, bg='white', fg='black')
        self.input_entry.grid(row=0, column=0, sticky="ew")
        self.input_entry.bind("<Return>", self.send_text_command)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_text_command)
        self.send_button.grid(row=0, column=1, padx=(5, 0))

        self.listen_button = tk.Button(self.input_frame, text="Listen", command=self.send_listen_command)
        self.listen_button.grid(row=0, column=2, padx=(5, 0))

        self.clear_button = tk.Button(self.input_frame, text="Clear", command=self.clear_history)
        self.clear_button.grid(row=0, column=3, padx=(5, 0))

        self.restart_button = tk.Button(self.input_frame, text="Restart", command=self.restart_application)
        self.restart_button.grid(row=0, column=4, padx=(5, 0))

        # --- PanedWindow Content ---

        # Left frame for functions
        self.functions_frame = tk.Frame(self.main_paned_window, bg='white')
        self.functions_frame.grid_rowconfigure(1, weight=1)
        self.functions_frame.grid_columnconfigure(0, weight=1)
        self.main_paned_window.add(self.functions_frame, width=200)

        # Middle frame for logs and output
        self.middle_paned_window = tk.PanedWindow(self.main_paned_window, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg='white')
        self.main_paned_window.add(self.middle_paned_window)

        # Log frame
        self.log_frame = tk.Frame(self.middle_paned_window, bg='white')
        self.log_frame.grid_rowconfigure(1, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.middle_paned_window.add(self.log_frame, height=250)

        # Output frame
        self.output_frame = tk.Frame(self.middle_paned_window, bg='white')
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.middle_paned_window.add(self.output_frame)

        # --- Widgets within the frames ---

        # Output text widget
        self.output_text = scrolledtext.ScrolledText(self.output_frame, bg='white', fg='black', state='disabled')
        self.output_text.grid(row=0, column=0, sticky="nsew")

        # Functions list widgets
        self.functions_label = tk.Label(self.functions_frame, text="功能列表", bg='white', font=('Arial', 12, 'bold'))
        self.functions_label.grid(row=0, column=0, pady=5, sticky="ew")
        self.functions_listbox = tk.Listbox(self.functions_frame, bg='white', fg='black', selectbackground='#cce5ff')
        self.functions_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        for name in self.program_mapping.keys():
            self.functions_listbox.insert(tk.END, name)

        # Logs view widgets
        self.logs_label = tk.Label(self.log_frame, text="日志记录", bg='white', font=('Arial', 12, 'bold'))
        self.logs_label.grid(row=0, column=0, pady=5, sticky="ew")
        self.logs_tree = ttk.Treeview(self.log_frame, show='tree')
        self.logs_tree.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self._populate_logs()

    def _populate_logs(self):
        log_file_path = "logs/application.json"
        if not os.path.exists(log_file_path):
            return

        # Clear existing logs
        for i in self.logs_tree.get_children():
            self.logs_tree.delete(i)

        logs_by_date = {}
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        # Try to parse as JSON
                        log_entry = json.loads(line)
                        timestamp = log_entry.get('timestamp', '')
                        message = log_entry.get('message', '')
                        date_str = timestamp.split('T')[0]
                    except (json.JSONDecodeError, AttributeError):
                        # Fallback for plain text lines
                        # Attempt to extract a date-like pattern from the start of the line
                        parts = line.split(' | ')
                        if len(parts) > 1 and len(parts[0]) > 10:
                            # Assuming format 'YYYY-MM-DD HH:MM:SS | ...'
                            date_str = parts[0][:10]
                            message = ' | '.join(parts[1:])
                        else:
                            # If no timestamp, use a generic key or skip
                            date_str = "Unknown Date"
                            message = line

                    if date_str not in logs_by_date:
                        logs_by_date[date_str] = []

                    # Remove time from the message if it's there
                    if len(message) > 9 and message[2] == ':' and message[5] == ':':
                         message = message[9:].lstrip()

                    logs_by_date[date_str].append(message)

        except Exception as e:
            logger.error(f"Failed to read or parse log file: {e}")
            return

        # Populate the treeview
        for date_str in sorted(logs_by_date.keys(), reverse=True):
            date_node = self.logs_tree.insert('', 'end', text=date_str, open=False)
            for msg in logs_by_date[date_str]:
                self.logs_tree.insert(date_node, 'end', text=msg)


    def set_command_callback(self, callback):
        self.command_callback = callback

    def send_text_command(self, event=None):
        command = self.input_entry.get().strip()
        if command and self.command_callback:
            logger.info(f"Sending text command: {command}")
            self.command_callback("text", command)
            self.input_entry.delete(0, tk.END)

    def send_listen_command(self):
        if self.command_callback:
            logger.info("Initiating voice command")
            self.command_callback("voice", None)

    def set_input_text(self, text):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, text)

    def clear_history(self):
        logger.info("Clearing history")
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')

    def restart_application(self):
        logger.info("Restarting application")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def append_to_history(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
