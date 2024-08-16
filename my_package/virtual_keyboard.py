import tkinter as tk
from pypinyin import lazy_pinyin, Style

# 创建主窗口
root = tk.Tk()
root.title("虚拟键盘与拼音，Shift，数字，和表情符号")

# 键盘按钮配置（小写）
keys_lower = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm']
]

# 键盘按钮配置（大写）
keys_upper = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
]

# 数字键盘配置
keys_numbers = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['0']
]

# 表情键盘配置
keys_emojis = [
    ['😊', '😂', '😍', '🥰', '😎'],
    ['😭', '😡', '😱', '👍', '👎'],
    ['🙌', '🙏', '👏', '💪', '🔥']
]

# 符号键盘配置
keys_symbols = [
    ['，', '。', '！', '？', '、'],
    ['：', '；', '（', '）', '【'],
    ['】', '‘', '’', '“', '”']
]

# 特殊按钮
special_keys = {
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
language_mode = 'EN'  # 默认英文输入
pinyin_buffer = ""  # 用于存储拼音输入
shift_mode = False  # 大小写模式标志
number_mode = False  # 数字模式标志
emoji_mode = False  # 表情模式标志
symbol_mode = False  # 符号模式标志

# 处理按钮按下事件
def on_key_press(value):
    global pinyin_buffer, shift_mode, number_mode, emoji_mode, symbol_mode
    
    if value == 'Backspace':
        entry_text.set(entry_text.get()[:-1])
    elif value == 'Enter':
        entry_text.set(entry_text.get() + '\n')
    elif value == 'Shift':
        shift_mode = not shift_mode
        update_keyboard()
    elif value == '123':
        number_mode = not number_mode
        emoji_mode = False  # 退出表情模式
        symbol_mode = False  # 退出符号模式
        update_keyboard()
    elif value == '😊':
        emoji_mode = not emoji_mode
        number_mode = False  # 退出数字模式
        symbol_mode = False  # 退出符号模式
        update_keyboard()
    elif value == '符':
        symbol_mode = not symbol_mode
        number_mode = False  # 退出数字模式
        emoji_mode = False  # 退出表情模式
        update_keyboard()    
    elif value == 'space':
        entry_text.set(entry_text.get() + ' ')
    elif value == '🌐':  # 切换中英文
        global language_mode
        if language_mode == 'EN':
            language_mode = 'CN'
            language_button.config(text="CN")
        else:
            language_mode = 'EN'
            language_button.config(text="EN")
    else:
        entry_text.set(entry_text.get() + value)

# 更新键盘上的字母显示（大小写切换/数字切换/表情切换）
def update_keyboard():
    if emoji_mode:
        for i, row in enumerate(keys_emojis):
            for j, key in enumerate(row):
                if j < len(buttons[i]):
                    buttons[i][j].config(text=key)
        # 隐藏不需要的字母键
        for i in range(len(keys_emojis), len(buttons)):
            for button in buttons[i]:
                button.grid_remove()
    elif symbol_mode:
        for i, row in enumerate(keys_symbols):
            for j, key in enumerate(row):
                if j < len(buttons[i]):
                    buttons[i][j].config(text=key)
        # 隐藏不需要的字母键
        for i in range(len(keys_symbols), len(buttons)):
            for button in buttons[i]:
                button.grid_remove()           
    elif number_mode:
        for i, row in enumerate(keys_numbers):
            for j, key in enumerate(row):
                if j < len(buttons[i]):
                    buttons[i][j].config(text=key)
        # 隐藏不需要的字母键
        for i in range(len(keys_numbers), len(buttons)):
            for button in buttons[i]:
                button.grid_remove()
    else:
        # 恢复字母键盘
        for i, row in enumerate(keys_lower if not shift_mode else keys_upper):
            for j, key in enumerate(row):
                buttons[i][j].config(text=key)
                buttons[i][j].grid()
        # 显示所有行
        for button_row in buttons:
            for button in button_row:
                button.grid()

# 创建显示输入内容的文本框
entry_text = tk.StringVar()
entry = tk.Entry(root, textvariable=entry_text, font=("Helvetica", 24))
entry.grid(row=0, column=0, columnspan=10)

# 创建键盘按钮
buttons = []
for i, row in enumerate(keys_lower):
    button_row = []
    for j, key in enumerate(row):
        button = tk.Button(root, text=key, width=5, height=2, font=("Helvetica", 18),
                           command=lambda key=key: on_key_press(key),
                           activebackground='lightblue', activeforeground='black')
        button.grid(row=i+1, column=j)
        button_row.append(button)
    buttons.append(button_row)

# 创建特殊功能键
special_button_row = len(keys_lower) + 1

# 左下角的123按钮
tk.Button(root, text=special_keys['123'], width=5, height=2, font=("Helvetica", 18),
          command=lambda: on_key_press(special_keys['123']),
          activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=0)

# 语言切换按钮
language_button = tk.Button(root, text="EN", width=5, height=2, font=("Helvetica", 18),
                            command=lambda: on_key_press('🌐'),
                            activebackground='lightblue', activeforeground='black')
language_button.grid(row=special_button_row, column=1)

# 中间的空格按钮
tk.Button(root, text=special_keys['space'], width=25, height=2, font=("Helvetica", 18),
          command=lambda: on_key_press(special_keys['space']),
          activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=2, columnspan=5)

# 右下角的表情按钮
tk.Button(root, text=special_keys['emoji'], width=5, height=2, font=("Helvetica", 18),
          command=lambda: on_key_press(special_keys['emoji']),
          activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=7)

# 右下角的符号按钮
tk.Button(root, text=special_keys['symbols'], width=5, height=2, font=("Helvetica", 18),
          command=lambda: on_key_press(special_keys['symbols']),
          activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=6)

# 右下角的换行按钮
tk.Button(root, text=special_keys['enter'], width=5, height=2, font=("Helvetica", 18),
          command=lambda: on_key_press(special_keys['enter']),
          activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=8)

# 右下角的删除按钮
tk.Button(root, text=special_keys['backspace'], width=5, height=2, font=("Helvetica", 18),
          command=lambda: on_key_press(special_keys['backspace']),
          activebackground='lightblue', activeforeground='black').grid(row=special_button_row, column=9)

# 右边的Shift按钮
tk.Button(root, text=special_keys['shift'], width=5, height=2, font=("Helvetica", 18),
          command=lambda: on_key_press(special_keys['shift']),
          activebackground='lightblue', activeforeground='black').grid(row=special_button_row - 1, column=9)

# 运行主循环
root.mainloop()
