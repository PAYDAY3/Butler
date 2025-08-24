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
        tk.Button(self, text=self.special_keys['space'], width=20, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['space']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=2, columnspan=4)

        # 右下角的符号按钮
        tk.Button(self, text=self.special_keys['symbols'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['symbols']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=6)

        # 右下角的表情按钮
        tk.Button(self, text=self.special_keys['emoji'], width=5, height=2, font=("Helvetica", 18),
                  command=lambda: self.on_key_press(self.special_keys['emoji']),
                  activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=7)

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

        self._build_button_grid()
        self.current_row = 0
        self.current_col = 0
        self.active = False
        # Deactivate navigation by default, main app will activate it.
        # self.activate_navigation()

    def _build_button_grid(self):
        all_children = self.winfo_children()
        button_info = []
        for child in all_children:
            if isinstance(child, tk.Button) and child.winfo_manager() == 'grid':
                info = child.grid_info()
                if info and 'row' in info and 'column' in info:
                    button_info.append((info['row'], info['column'], child))

        if not button_info:
            self.button_grid = []
            return

        button_info.sort()
        max_row = max(info[0] for info in button_info)
        max_col = max(info[1] for info in button_info)

        # Adjust for 0-based index if buttons start at row 1
        row_offset = min(info[0] for info in button_info)

        grid = [[None] * (max_col + 1) for _ in range(max_row - row_offset + 1)]

        for r, c, button in button_info:
            grid[r - row_offset][c] = button

        self.button_grid = [row for row in grid if any(row)]

    def update_keyboard(self):
        if self.emoji_mode:
            keys = self.keys_emojis
        elif self.symbol_mode:
            keys = self.keys_symbols
        elif self.number_mode:
            keys = self.keys_numbers
        else:
            keys = self.keys_lower if not self.shift_mode else self.keys_upper

        for i, row in enumerate(self.buttons):
            for j, button in enumerate(row):
                if i < len(keys) and j < len(keys[i]):
                    button.config(text=keys[i][j])
                    button.grid()
                else:
                    button.grid_remove()

        self._build_button_grid()

    def activate_navigation(self):
        self.active = True
        self.bind("<Up>", self.navigate_keyboard)
        self.bind("<Down>", self.navigate_keyboard)
        self.bind("<Left>", self.navigate_keyboard)
        self.bind("<Right>", self.navigate_keyboard)
        self.bind("<Return>", self.press_key)
        self.button_grid[self.current_row][self.current_col].focus_set()

    def deactivate_navigation(self):
        self.active = False
        self.unbind("<Up>")
        self.unbind("<Down>")
        self.unbind("<Left>")
        self.unbind("<Right>")
        self.unbind("<Return>")

    def navigate_keyboard(self, event):
        if not self.active:
            return

        rows = len(self.button_grid)
        if not rows: return

        cols = len(self.button_grid[self.current_row])

        if event.keysym == 'Down':
            self.current_row = (self.current_row + 1) % rows
        elif event.keysym == 'Up':
            self.current_row = (self.current_row - 1 + rows) % rows
        elif event.keysym == 'Right':
            self.current_col = (self.current_col + 1) % cols
        elif event.keysym == 'Left':
            self.current_col = (self.current_col - 1 + cols) % cols

        # Find next available button in the new row/col
        # This is a simple implementation, it might not be perfect for all layouts.
        while self.button_grid[self.current_row][self.current_col] is None:
            if event.keysym == 'Right':
                self.current_col = (self.current_col + 1) % cols
            elif event.keysym == 'Left':
                self.current_col = (self.current_col - 1 + cols) % cols
            else: # Up/Down
                # This part is tricky. A simple linear search might be confusing.
                # For now, we just land on the first available button in the row.
                try:
                    self.current_col = next(i for i, v in enumerate(self.button_grid[self.current_row]) if v is not None)
                except StopIteration:
                    # Row has no buttons, this shouldn't happen with the current build_grid logic.
                    # We can try to find another row.
                    return

        self.button_grid[self.current_row][self.current_col].focus_set()

    def press_key(self, event):
        if not self.active:
            return

        focused_widget = self.focus_get()
        if isinstance(focused_widget, tk.Button):
            focused_widget.invoke()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Virtual Keyboard")
    keyboard = VirtualKeyboard(root)
    keyboard.pack()
    root.mainloop()
