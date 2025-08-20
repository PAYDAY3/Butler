import tkinter as tk
from pypinyin import lazy_pinyin, Style

class VirtualKeyboard(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        # 键盘按钮配置（小写）
        self.keys_lower = [
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm']
        ]

        # 键盘按钮配置（大写）
        self.keys_upper = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]

        # 数字键盘配置
        self.keys_numbers = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0']
        ]

        # 表情键盘配置
        self.keys_emojis = [
            ['😊', '😂', '😍', '🥰', '😎'],
            ['😭', '😡', '😱', '👍', '👎'],
            ['🙌', '🙏', '👏', '💪', '🔥']
        ]

        # 符号键盘配置
        self.keys_symbols = [
            ['，', '。', '！', '？', '、'],
            ['：', '；', '（', '）', '【'],
            ['】', '‘', '’', '“', '”']
        ]

        # 特殊按钮
        self.special_keys = {
            'space': ' ',
            'shift': 'Shift',
            'enter': 'Enter',
            'backspace': 'Backspace',
            '123': '123',
            'emoji': '😊',
            'symbols': '符',
            'language': '🌐'
        }

        # 全局变量
        self.language_mode = 'EN'  # 默认英文输入
        self.pinyin_buffer = ""  # 用于存储拼音输入
        self.shift_mode = False  # 大小写模式标志
        self.number_mode = False  # 数字模式标志
        self.emoji_mode = False  # 表情模式标志
        self.symbol_mode = False  # 符号模式标志

        self.entry_text = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # 创建显示输入内容的文本框
        entry = tk.Entry(self, textvariable=self.entry_text, font=("Helvetica", 24))
        entry.grid(row=0, column=0, columnspan=10)

        # 创建键盘按钮
        self.buttons = []
        for i, row in enumerate(self.keys_lower):
            button_row = []
            for j, key in enumerate(row):
                button = tk.Button(self, text=key, width=5, height=2, font=("Helvetica", 18),
                                   command=lambda key=key: self.on_key_press(key),
                                   activebackground='lightblue', activeforeground='black')
                button.grid(row=i+1, column=j)
                button_row.append(button)
            self.buttons.append(button_row)

        # 创建特殊功能键
        special_button_row = len(self.keys_lower) + 1

        # 左下角的123按钮
        tk.Button(self, text=self.special_keys['123'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['123']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=0)

        # 语言切换按钮
        self.language_button = tk.Button(self, text="EN", width=5, height=2, font=("Helvetica", 18),
                                    command=lambda: self.on_key_press('🌐'),
                                    activebackground='lightblue', activeforeground='black')
        self.language_button.grid(row=special_button_row, column=1)

        # 中间的空格按钮
        tk.Button(self, text=self.special_keys['space'], width=25, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['space']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=2, columnspan=5)

        # 右下角的表情按钮
        tk.Button(self, text=self.special_keys['emoji'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['emoji']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=7)

        # 右下角的符号按钮
        tk.Button(self, text=self.special_keys['symbols'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['symbols']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=6)

        # 右下角的换行按钮
        tk.Button(self, text=self.special_keys['enter'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['enter']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=8)

        # 右下角的删除按钮
        tk.Button(self, text=self.special_keys['backspace'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['backspace']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=9)

        # 右边的Shift按钮
        tk.Button(self, text=self.special_keys['shift'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['shift']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row - 1, column=9)


    def on_key_press(self, value):
        if value == 'Backspace':
            self.entry_text.set(self.entry_text.get()[:-1])
        elif value == 'Enter':
            self.entry_text.set(self.entry_text.get() + '\n')
        elif value == 'Shift':
            self.shift_mode = not self.shift_mode
            self.update_keyboard()
        elif value == '123':
            self.number_mode = not self.number_mode
            self.emoji_mode = False  # 退出表情模式
            self.symbol_mode = False  # 退出符号模式
            self.update_keyboard()
        elif value == '😊':
            self.emoji_mode = not self.emoji_mode
            self.number_mode = False  # 退出数字模式
            self.symbol_mode = False  # 退出符号模式
            self.update_keyboard()
        elif value == '符':
            self.symbol_mode = not self.symbol_mode
            self.number_mode = False  # 退出数字模式
            self.emoji_mode = False  # 退出表情模式
            self.update_keyboard()
        elif value == 'space':
            self.entry_text.set(self.entry_text.get() + ' ')
        elif value == '🌐':  # 切换中英文
            if self.language_mode == 'EN':
                self.language_mode = 'CN'
                self.language_button.config(text="CN")
            else:
                self.language_mode = 'EN'
                self.language_button.config(text="EN")
        else:
            self.entry_text.set(self.entry_text.get() + value)

    def update_keyboard(self):
        if self.emoji_mode:
            for i, row in enumerate(self.keys_emojis):
                for j, key in enumerate(row):
                    if j < len(self.buttons[i]):
                        self.buttons[i][j].config(text=key)
            # 隐藏不需要的字母键
            for i in range(len(self.keys_emojis), len(self.buttons)):
                for button in self.buttons[i]:
                    button.grid_remove()
        elif self.symbol_mode:
            for i, row in enumerate(self.keys_symbols):
                for j, key in enumerate(row):
                    if j < len(self.buttons[i]):
                        self.buttons[i][j].config(text=key)
            # 隐藏不需要的字母键
            for i in range(len(self.keys_symbols), len(self.buttons)):
                for button in self.buttons[i]:
                    button.grid_remove()
        elif self.number_mode:
            for i, row in enumerate(self.keys_numbers):
                for j, key in enumerate(row):
                    if j < len(self.buttons[i]):
                        self.buttons[i][j].config(text=key)
            # 隐藏不需要的字母键
            for i in range(len(self.keys_numbers), len(self.buttons)):
                for button in self.buttons[i]:
                    button.grid_remove()
        else:
            # 恢复字母键盘
            keys = self.keys_lower if not self.shift_mode else self.keys_upper
            for i, row in enumerate(keys):
                for j, key in enumerate(row):
                    self.buttons[i][j].config(text=key)
                    self.buttons[i][j].grid()
            # 显示所有行
            for button_row in self.buttons:
                for button in button_row:
                    button.grid()

    def get_text(self):
        return self.entry_text.get()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Virtual Keyboard")
    keyboard = VirtualKeyboard(root)
    keyboard.pack()
    root.mainloop()
