import tkinter as tk
from package.weather import get_weather_from_web
from package.virtual_keyboard import VirtualKeyboard

class WeatherApp(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Weather App")
        self.geometry("800x600")

        # Create main frames
        self.weather_frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        self.weather_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.keyboard_frame = tk.Frame(self)
        self.keyboard_frame.pack(side=tk.BOTTOM, fill=tk.X)

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

def run(master=None):
    if master is None:
        root = tk.Tk()
        app = WeatherApp(root)
        root.withdraw() # Hide the root window
        app.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
        root.mainloop()
    else:
        app = WeatherApp(master)

if __name__ == "__main__":
    run()
