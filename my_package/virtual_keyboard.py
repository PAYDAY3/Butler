import tkinter as tk
from tkinter import ttk

class VirtualKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("虚拟键盘")
        self.is_uppercase = True   # 用于跟踪当前是否为大写模式
        
        self.text_input = tk.Text(self.root, height=5, width=50)
        self.text_input.grid(row=0, column=0, columnspan=15, padx=10, pady=10)
        
        self.keyboard_window = tk.Toplevel(self.root)
        self.keyboard_window.title("虚拟键盘")
        self.keyboard_window.protocol("WM_DELETE_WINDOW", self.hide_keyboard)  # 点击关闭按钮时隐藏键盘
        self.tabControl = ttk.Notebook(self.root)
        self.init_keyboard()
        self.init_function_panel()

        self.tabControl.grid(row=2, column=0, columnspan=15, padx=10, pady=10)
        self.track_input_boxes()

    def init_keyboard(self):
        # 创建字母面板
        self.letters_frame = ttk.Frame(self.tabControl)
        self.create_button_row("QWERTYUIOP", 1, self.letters_frame)
        self.create_button_row("ASDFGHJKL", 2, self.letters_frame)
        self.create_button_row("ZXCVBNM", 3, self.letters_frame)
        self.tabControl.add(self.letters_frame, text='Letters')
        
        # 创建数字面板
        self.numbers_frame = ttk.Frame(self.tabControl)
        self.create_number_row("12345", 1, self.numbers_frame)
        self.create_number_row("67890", 2, self.numbers_frame)
        self.tabControl.add(self.numbers_frame, text='数')

        # 创建符号面板
        self.symbols_frame = ttk.Frame(self.tabControl)
        self.create_symbol_row("@#$%", 1, self.symbols_frame)
        self.create_symbol_row("()_-+", 2, self.symbols_frame)
        self.create_symbol_row(".,?!", 3, self.symbols_frame)
        self.tabControl.add(self.symbols_frame, text='符')
        
        # 创建额外面板
        self.extra_frame = ttk.Frame(self.tabControl)
        self.create_extra_buttons(self.extra_frame)
        # 添加额外面板到tabControl并设置为默认显示面板
        self.tabControl.add(self.extra_frame, text='额外', state='normal') 

        # 设置tabControl的默认显示面板为额外面板
        self.tabControl.select(self.extra_frame)
        # 重写tabControl的select方法，使其不自动隐藏其他面板
        
        def select_without_hiding(tab):
            self.tabControl.select(tab)

        # 将select方法替换为自定义的select_without_hiding方法
        self.tabControl.select = select_without_hiding      
          
    def init_function_panel(self):
        # 创建功能面板
        self.function_frame = ttk.Frame(self.tabControl)
        
        self.delete_btn = tk.Button(self.function_frame, text="删除", command=self.delete_character)
        self.delete_btn.grid(row=0, column=0, padx=5, pady=10)

        self.toggle_case_btn = tk.Button(self.function_frame, text="大/小", command=self.toggle_case)
        self.toggle_case_btn.grid(row=0, column=1, padx=5, pady=10)
        
        self.size_slider = tk.Scale(self.function_frame, from_=8, to=32, orient=tk.HORIZONTAL, label="字体大小", command=self.adjust_button_size)
        self.size_slider.set(12)   # 设置默认字体大小
        self.size_slider.grid(row=0, column=2, columnspan=4, sticky="we", padx=5, pady=10)

        self.enter_btn = tk.Button(self.function_frame, text="回车", command=self.enter_pressed)
        self.enter_btn.grid(row=0, column=6, columnspan=2, padx=5, pady=10)
        
        self.space_btn = tk.Button(self.function_frame, text="空格", command=lambda: self.on_button_click(" "))
        self.space_btn.grid(row=0, column=8, columnspan=4, padx=5, pady=10)
        
        self.copy_btn = tk.Button(self.function_frame, text="复制", command=self.copy_text)
        self.copy_btn.grid(row=0, column=12, padx=5, pady=10)

        self.paste_btn = tk.Button(self.function_frame, text="粘贴", command=self.paste_text)
        self.paste_btn.grid(row=0, column=13, padx=5, pady=10)

        self.left_arrow_btn = tk.Button(self.function_frame, text="←", command=lambda: self.move_cursor(-1))
        self.left_arrow_btn.grid(row=0, column=14, padx=5, pady=10)

        self.right_arrow_btn = tk.Button(self.function_frame, text="→", command=lambda: self.move_cursor(1))
        self.right_arrow_btn.grid(row=0, column=15, padx=5, pady=10)

        self.clear_btn = tk.Button(self.function_frame, text="清空", command=self.clear_text)
        self.clear_btn.grid(row=0, column=16, padx=5, pady=10)
        # 添加跳转按钮到功能面板
        self.switch_to_letters_btn = tk.Button(self.function_frame, text="字母面板", command=self.switch_to_letters_panel)
        self.switch_to_letters_btn.grid(row=1, column=0, columnspan=17, padx=5, pady=10)
        
        self.tabControl.add(self.function_frame, text='功能')
        
    def switch_to_letters_panel(self):
        self.tabControl.select(self.letters_frame)
                
    def delete_character(self):
        try:
            cursor_position = self.text_input.index(tk.INSERT)
            if cursor_position != "1.0":
                self.text_input.delete(f"{cursor_position} - 1c", cursor_position)
        except tk.TclError:
            pass

    def adjust_button_size(self, event=None):
        font_size = self.size_slider.get()
        for frame in [self.letters_frame, self.numbers_frame, self.symbols_frame, self.extra_frame]:
            for child in frame.winfo_children():
                if isinstance(child, tk.Button):
                    child.config(font=("TkDefaultFont", font_size))

    def create_button_row(self, letters, row, frame):
        for i, letter in enumerate(letters):
            btn = tk.Button(frame, text=letter, command=lambda l=letter: self.on_button_click(l))
            btn.grid(row=row, column=i, padx=3, pady=3)
            
    def create_extra_buttons(self, frame):
        extra_buttons = ["{", "}", "[", "]", "|", "\\", ";", ":", "'", "\"", "<", ">", "/", "*", "&", "^", "%", "$", "#", "!", "~"]
        for i, button in enumerate(extra_buttons):
            row = i // 12 + 1  # 每行12个按钮
            col = i % 12
            btn = tk.Button(frame, text=button, command=lambda b=button: self.on_button_click(b))
            btn.grid(row=row, column=col, padx=3, pady=3)
            
    def create_number_row(self, numbers, row, frame):
        for i, number in enumerate(numbers):
            btn = tk.Button(frame, text=number, command=lambda n=number: self.on_button_click(n))
            btn.grid(row=row, column=i, padx=3, pady=3)

    def create_symbol_row(self, symbols, row, frame):
        for i, symbol in enumerate(symbols):
            btn = tk.Button(frame, text=symbol, command=lambda s=symbol: self.on_button_click(s))
            btn.grid(row=row, column=i, padx=3, pady=3)
            
    def track_input_boxes(self):
        """跟踪所有输入框，并在点击时自动打开虚拟键盘"""
        for widget in self.root.winfo_children():
            if isinstance(widget, (tk.Text, tk.Entry)):
                widget.bind("<FocusIn>", self.show_keyboard)

    def show_keyboard(self, event=None):
        """显示虚拟键盘"""
        self.text_input = event.widget  # 设置当前跟踪的输入框
        self.keyboard_window.deiconify()  # 显示键盘窗口

    def hide_keyboard(self):
        """隐藏虚拟键盘"""
        self.keyboard_window.withdraw()
        
    def on_button_click(self, char):
        if self.text_input:
            self.text_input.insert(tk.END, char)
            self.text_input.focus()  # 确保输入框保持焦点
            
    def toggle_case(self):
        self.is_uppercase = not self.is_uppercase   # 切换大小写模式
        self.update_button_labels()   # 更新按钮文本
        # 更新切换大小写按钮的文本提示当前模式
        self.toggle_case_btn.config(text="小" if self.is_uppercase else "大")

    def update_button_labels(self):
        for frame in [self.letters_frame, self.numbers_frame, self.symbols_frame]:
            for child in frame.winfo_children():
                if isinstance(child, tk.Button):
                    letter = child["text"]
                    new_text = letter.upper() if self.is_uppercase else letter.lower()   # 根据当前大小写模式设置按钮文本
                    child.config(text=new_text)
                    
    def enter_pressed(self):
        self.text_input.insert(tk.END, "\n") 
        
    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text_input.get("1.0", tk.END))

    def paste_text(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.text_input.insert(tk.END, clipboard_text)
        except tk.TclError:
            pass 

    def move_cursor(self, offset):
        try:
            cursor_position = self.text_input.index(tk.INSERT)
            new_position = f"{int(cursor_position.split('.')[0])}.{int(cursor_position.split('.')[1]) + offset}"
            self.text_input.mark_set(tk.INSERT, new_position)
        except tk.TclError:
            pass
        
    def clear_text(self):
        self.text_input.delete("1.0", tk.END)       
        
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualKeyboard(root)
    root.mainloop()
