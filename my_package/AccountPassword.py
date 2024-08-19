import sqlite3
import pyautogui
import time
import sys
from getpass import getpass
import bcrypt
from jarvis.jarvis import takecommand # 语音识别
from my_package import Logging

logging = Logging.getLogge(__naneme__)

# 初始化数据库连接
conn = sqlite3.connect('account_manager.db')
cursor = conn.cursor()

# 创建用户表结构，添加 website 字段
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    category TEXT NOT NULL,
                    website TEXT NOT NULL
                 )''')
conn.commit()

# 自动登录功能
def auto_login():
    cursor.execute("SELECT id, username, category, website FROM users")
    accounts = cursor.fetchall()

    if accounts:
        print("可用账号列表:")
        for i, account in enumerate(accounts):
            print(f"{i+1}. {account[1]} ({account[2]}) - {account[3]}")

        choice = input("请输入要自动登录的账号编号: ")

        if choice.strip() == "":
            return False  # 用户跳过自动登录

        try:
            account_id = accounts[int(choice) - 1][0]  # 获取选择的账号ID
        except (ValueError, IndexError):
            print("无效的选择，请重试。")
            return False  # 无效选择后跳过自动登录

        cursor.execute("SELECT username, password, website FROM users WHERE id = ?", (account_id,))
        user = cursor.fetchone()

        if user:
            username, hashed_password, website = user
            password = getpass(f"请输入 {website} 的密码以自动登录: ")

            # 验证密码
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                print(f"自动登录 {username} 到 {website}...")
                
                # 记录日志
                logging.info(f"用户 {username} 登录了网站 {website}")
                
                time.sleep(2)
                
                pyautogui.write(username)
                pyautogui.press('tab')
                pyautogui.write(password)
                pyautogui.press('enter')
                
                print("登录操作已完成，程序将退出。")
                sys.exit()  # 登录完成后退出程序
            else:
                print("密码错误，无法自动登录。")
                return False  # 密码错误后跳过自动登录
        else:
            print("无法找到指定用户。")
            return False  # 用户未找到后跳过自动登录
    else:
        print("没有找到任何账号，无法自动登录。")
        return False  # 没有账号时跳过自动登录

# 创建新账号
def create_account():
    username = input("请输入用户名: ")
    
    if len(username) < 3:
        print("用户名长度必须大于3个字符。")
        return
    
    password = getpass("请输入密码: ")
    
    # 对密码进行加密
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    category = input("请输入账号分类 (如社交媒体, 工作, 娱乐): ")
    website = input("请输入网站地址 (如 https://example.com): ")

    try:
        cursor.execute("INSERT INTO users (username, password, category, website) VALUES (?, ?, ?, ?)", 
                       (username, hashed_password, category, website))
        conn.commit()
        print("账号创建成功!")
    except sqlite3.IntegrityError:
        print("用户名已存在，请选择其他用户名。")

# 修改密码（允许修改指定的账号密码）
def change_password():
    username = input("请输入要修改密码的用户名: ")
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        new_password = getpass("请输入新密码: ")
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user[0]))
        conn.commit()
        print(f"{username} 的密码修改成功!")
    else:
        print("未找到指定用户名，请检查输入。")

# 修改账号分类
def change_category(user_id):
    new_category = input("请输入新的账号分类: ")
    cursor.execute("UPDATE users SET category = ? WHERE id = ?", (new_category, user_id))
    conn.commit()
    print("账号分类修改成功!")

# 修改网站地址
def change_website(user_id):
    new_website = input("请输入新的网站地址: ")
    cursor.execute("UPDATE users SET website = ? WHERE id = ?", (new_website, user_id))
    conn.commit()
    print("网站地址修改成功!")

# 删除指定的账号
def delete_account():
    username = input("请输入要删除的用户名: ")
    password = getpass("请输入要删除的密码: ")

    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        cursor.execute("DELETE FROM users WHERE id = ?", (user[0],))
        conn.commit()
        print(f"账号 {username} 已成功删除。")
    else:
        print("用户名或密码错误，无法删除账号。")

# 按分类查看账号
def view_accounts_by_category():
    category = input("请输入要查看的分类: ")
    cursor.execute("SELECT username, website FROM users WHERE category = ?", (category,))
    accounts = cursor.fetchall()
    
    if accounts:
        print(f"\n分类 '{category}' 下的账号:")
        for account in accounts:
            print(f"用户名: {account[0]} - 网站: {account[1]}")
    else:
        print(f"分类 '{category}' 下没有找到账号。")

# 处理用户选择
def process_choice(choice):
    if choice == '登录':
        auto_login()
    elif choice == '创建':
        create_account()
    elif choice == '修改密码':
        change_password()
    elif choice == '修改分类':
        user_id = int(input("请输入要修改分类的账号ID: "))
        change_category(user_id)
    elif choice == '修改网站':
        user_id = int(input("请输入要修改网站的账号ID: "))
        change_website(user_id)
    elif choice == '删除':
        delete_account()
    elif choice == '查看':
        view_accounts_by_category()
    elif choice == '退出':
        print("退出程序。")
        sys.exit()
    else:
        print("无效的选择，请重试。")

# 主菜单
def AccountPassword():
    while True:
        print("\n----- 账号密码管理程序 -----")
        print("您可以通过说 '登录'、'创建'、'修改密码'、'修改分类'、'修改网站'、'删除'、'查看' 或 '退出' 来进行操作。")
        print("输入 '语音控制' 来使用语音控制，或直接输入命令进行操作。")

        choice = input("请选择操作方式 ('语音控制' 或 '文字输入'): ").strip().lower()

        if choice == '语音控制':
            command = takecommand()
            process_choice(command)
        elif choice == '文字输入':
            command = input("请输入您的命令: ").strip().lower()
            process_choice(command)
        else:
            print("无效的选择，请重试。")

# 程序启动时尝试自动登录
if not auto_login():  # 如果自动登录失败或跳过，启动主菜单
    AccountPassword()