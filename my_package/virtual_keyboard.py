import tkinter as tk
from tkinter import ttk

class VirtualKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("虚拟键盘")
        self.is_uppercase = True  # 用于跟踪当前是否为大写模式
        
        self.text_input = tk.Entry(self.root)
        self.text_input.grid(row=0, column=0, columnspan=6)

        self.tabControl = ttk.Notebook(self.root)
        self.init_keyboard()
        self.delete_btn = tk.Button(self.root, text="删除", command=self.delete_character)
        self.delete_btn.grid(row=2, column=0, pady=10)
           
        # 添加切换大小写的按钮
        self.toggle_case_btn = tk.Button(self.root, text="大/小", command=self.toggle_case)
        self.toggle_case_btn.grid(row=2, column=0, pady=10)
        
        # 添加字体大小调节的滑动条
        self.size_slider = tk.Scale(self.root, from_=8, to=32, orient=tk.HORIZONTAL, label="字体大小", command=self.adjust_button_size)
        self.size_slider.set(12)  # 设置默认字体大小
        self.size_slider.grid(row=2, column=1, columnspan=5, sticky="we")

    def init_keyboard(self):
        # 创建字母面板
        self.letters_frame = ttk.Frame(self.tabControl)
        self.create_button_row("QWERTYUIOP", 1, self.letters_frame)
        self.create_button_row("ASDFGHJKL", 2, self.letters_frame)
        self.create_button_row("ZXCVBNM", 3, self.letters_frame)
        self.create_button_row("qwertyuiop", 4, self.letters_frame)  # 添加小写字母行
        self.create_button_row("asdfghjkl", 5, self.letters_frame)  # 添加小写字母行
        self.create_button_row("zxcvbnm", 6, self.letters_frame)  # 添加小写字母行
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
        
        self.tabControl.grid(row=1, column=0, columnspan=6)
        
    def delete_character(self):
        current_text = self.text_input.get()
        cursor_position = self.text_input.index(tk.INSERT)  # 获取光标位置
        if cursor_position > 0:
            updated_text = current_text[:cursor_position-1] + current_text[cursor_position:]  # 删除光标前的字符
            self.text_input.delete(0, tk.END)  # 清空输入框
            self.text_input.insert(0, updated_text)  # 更新输入框内容
            self.text_input.icursor(cursor_position-1)  # 移动光标到删除后的位置

    def adjust_button_size(self, event=None):
        font_size = self.size_slider.get()
        for frame in [self.letters_frame, self.numbers_frame, self.symbols_frame]:
            for child in frame.winfo_children():
                if isinstance(child, tk.Button):
                    child.config(font=("TkDefaultFont", font_size))
                    # 可以根据需要调整按钮的宽度和高度
                    # child.config(width=new_width, height=new_height)
                    
    def create_button_row(self, letters, row, frame):
        for i, letter in enumerate(letters):
            btn = tk.Button(frame, text=letter, command=lambda l=letter: self.on_button_click(l))
            btn.grid(row=row, column=i, padx=3, pady=3)

    def create_number_row(self, numbers, row, frame):
        for i, number in enumerate(numbers):
            btn = tk.Button(frame, text=number, command=lambda n=number: self.on_button_click(n))
            btn.grid(row=row, column=i, padx=3, pady=3)

    def create_symbol_row(self, symbols, row, frame):
        for i, symbol in enumerate(symbols):
            btn = tk.Button(frame, text=symbol, command=lambda s=symbol: self.on_button_click(s))
            btn.grid(row=row, column=i, padx=3, pady=3)

    def on_button_click(self, char):
        self.text_input.insert(tk.END, char)

    def toggle_case(self):
        self.is_uppercase = not self.is_uppercase  # 切换大小写模式
        self.update_button_labels()  # 更新按钮文本
        # 更新切换大小写按钮的文本提示当前模式
        self.toggle_case_btn.config(text="小" if self.is_uppercase else "大")

    def update_button_labels(self):
        for frame in [self.letters_frame, self.numbers_frame, self.symbols_frame]:
            for child in frame.winfo_children():
                if isinstance(child, tk.Button):
                    letter = child["text"]
                    new_text = letter.upper() if self.is_uppercase else letter.lower()  # 根据当前大小写模式设置按钮文本
                    child.config(text=new_text)
                
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualKeyboard(root)
    root.mainloop()
    