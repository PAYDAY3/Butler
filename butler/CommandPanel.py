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
        self.functions_listbox.insert(tk.END, "天气预报")
        for name in self.program_mapping.keys():
            self.functions_listbox.insert(tk.END, name)
        self.functions_listbox.bind("<Double-1>", self.launch_selected_function)

    def launch_selected_function(self, event=None):
        selected_indices = self.functions_listbox.curselection()
        if not selected_indices:
            return

        selected_name = self.functions_listbox.get(selected_indices[0])

        if selected_name == "天气预报":
            WeatherApp(self.master)
            return

        program_file = self.program_mapping.get(selected_name)

        if program_file and self.command_callback:
            logger.info(f"Launching program: {selected_name} -> {program_file}")
            self.command_callback("launch_program", program_file)

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

from package.weather import get_weather_from_web
from package.virtual_keyboard import VirtualKeyboard

class WeatherApp(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Weather App")
        self.geometry("800x600")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main frames
        self.weather_frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        self.weather_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.keyboard_frame = tk.Frame(self)
        self.keyboard_frame.grid(row=1, column=0, sticky="nsew", padx=10)

        self.create_weather_widgets()

        # Add virtual keyboard
        self.keyboard = VirtualKeyboard(self.keyboard_frame)
        self.keyboard.pack()

        # Link keyboard to city entry
        self.keyboard.entry_text = self.city_entry_str

    def create_weather_widgets(self):
        # City entry
        self.city_entry_str = tk.StringVar()
        self.city_entry = tk.Entry(self.weather_frame, textvariable=self.city_entry_str, font=("Helvetica", 24))
        self.city_entry.pack(pady=10)

        # Search button
        self.search_button = tk.Button(self.weather_frame, text="Search", command=self.search_weather)
        self.search_button.pack(pady=5)

        # Weather display
        self.weather_summary_label = tk.Label(self.weather_frame, text="", font=("Helvetica", 18))
        self.weather_summary_label.pack(pady=10)

        # Details button
        self.details_button = tk.Button(self.weather_frame, text="Details", command=self.show_details, state=tk.DISABLED)
        self.details_button.pack(pady=5)

    def search_weather(self):
        city = self.city_entry.get()
        if city:
            weather_info = get_weather_from_web(city)
            if weather_info:
                summary = f"{weather_info['description']}, {weather_info['temperature']}°C"
                self.weather_summary_label.config(text=summary)
                self.details_button.config(state=tk.NORMAL)
                self.weather_info = weather_info
            else:
                self.weather_summary_label.config(text="Weather not found.")
                self.details_button.config(state=tk.DISABLED)

    def show_details(self):
        details_window = tk.Toplevel(self)
        details_window.title("Weather Details")
        details_window.geometry("400x300")

        if hasattr(self, 'weather_info'):
            details_text = f"Temperature: {self.weather_info['temperature']}°C\n" \
                           f"Description: {self.weather_info['description']}\n" \
                           f"Humidity: {self.weather_info['humidity']}\n" \
                           f"Wind: {self.weather_info['wind']}"

            details_label = tk.Label(details_window, text=details_text, font=("Helvetica", 16), justify=tk.LEFT)
            details_label.pack(padx=20, pady=20)

    def switch_focus(self, event):
        if self.active_frame == self.weather_frame:
            self.active_frame = self.keyboard_frame
            self.keyboard.activate_navigation()
            self.keyboard.button_grid[self.keyboard.current_row][self.keyboard.current_col].focus_set()
            self.deactivate_weather_navigation()
        else:
            self.active_frame = self.weather_frame
            self.keyboard.deactivate_navigation()
            self.activate_weather_navigation()
            self.focusable_widgets[self.current_focus_index].focus_set()

    def navigate(self, event):
        if self.active_frame == self.weather_frame:
            if event.keysym == "Down":
                self.current_focus_index = (self.current_focus_index + 1) % len(self.focusable_widgets)
            elif event.keysym == "Up":
                self.current_focus_index = (self.current_focus_index - 1) % len(self.focusable_widgets)

            self.focusable_widgets[self.current_focus_index].focus_set()

    def activate_widget(self, event):
        if self.active_frame == self.weather_frame:
            widget = self.focus_get()
            if isinstance(widget, tk.Button):
                widget.invoke()

    def activate_weather_navigation(self):
        self.bind("<Up>", self.navigate)
        self.bind("<Down>", self.navigate)
        self.bind("<Return>", self.activate_widget)

    def deactivate_weather_navigation(self):
        self.unbind("<Up>")
        self.unbind("<Down>")
        self.unbind("<Return>")
