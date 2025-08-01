import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import hashlib

class SimpleFileEncryptor:
    def __init__(self):
        self.key_file = "encryption_key.bin"
        self.audit_log = "encryption_log.txt"
    
    def log_operation(self, operation, file_path, status):
        """记录操作日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {operation}: {file_path} -> {status}\n"
        
        try:
            with open(self.audit_log, "a") as f:
                f.write(log_entry)
            return True
        except Exception:
            return False
    
    def generate_key(self, password=None):
        """生成或派生加密密钥"""
        try:
            if password:
                # 使用密码派生密钥
                salt = get_random_bytes(16)
                key = PBKDF2(password, salt, dkLen=16, count=100000)
                
                # 保存salt和密钥
                with open(self.key_file, 'wb') as f:
                    f.write(salt + key)
                return key
            else:
                # 生成随机密钥
                key = get_random_bytes(16)
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                return key
        except Exception as e:
            print(f"生成密钥时出错: {str(e)}")
            return None
    
    def load_key(self, password=None):
        """从文件加载密钥"""
        try:
            with open(self.key_file, 'rb') as f:
                key_data = f.read()
                
            if password:
                # 从文件读取salt和密钥
                salt = key_data[:16]
                stored_key = key_data[16:]
                # 重新派生密钥
                derived_key = PBKDF2(password, salt, dkLen=16, count=100000)
                
                # 验证派生密钥是否匹配
                if derived_key == stored_key:
                    return derived_key
                else:
                    print("密码错误，请重试")
                    return None
            else:
                # 直接返回随机密钥
                return key_data
        except FileNotFoundError:
            print("找不到密钥文件")
            return None
        except Exception as e:
            print(f"加载密钥失败: {str(e)}")
            return None
    
    def encrypt_file(self, file_path, key):
        """加密文件"""
        try:
            # 创建加密器
            cipher = AES.new(key, AES.MODE_CBC)
            iv = cipher.iv
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # 加密数据
            ciphertext = cipher.encrypt(pad(data, AES.block_size))
            
            # 写入加密文件
            encrypted_file = file_path + '.enc'
            with open(encrypted_file, 'wb') as f:
                f.write(iv)
                f.write(ciphertext)
            
            # 记录日志
            self.log_operation("加密", file_path, "成功")
            
            print(f"文件加密成功: {encrypted_file}")
            return encrypted_file
        except Exception as e:
            self.log_operation("加密", file_path, f"失败: {str(e)}")
            print(f"加密文件时出错: {str(e)}")
            return None
    
    def decrypt_file(self, file_path, key):
        """解密文件"""
        try:
            # 检查文件扩展名
            if not file_path.endswith('.enc'):
                print("注意: 文件扩展名不是.enc，可能不是加密文件")
            
            # 读取加密文件
            with open(file_path, 'rb') as f:
                iv = f.read(16)  # AES块大小是16字节
                ciphertext = f.read()
            
            # 创建解密器
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 解密数据
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
            
            # 生成解密文件名
            if file_path.endswith('.enc'):
                decrypted_file = file_path[:-4]
            else:
                decrypted_file = file_path + '.dec'
            
            # 避免覆盖已有文件
            if os.path.exists(decrypted_file):
                base, ext = os.path.splitext(decrypted_file)
                counter = 1
                while os.path.exists(f"{base}_{counter}{ext}"):
                    counter += 1
                decrypted_file = f"{base}_{counter}{ext}"
            
            # 写入解密文件
            with open(decrypted_file, 'wb') as f:
                f.write(plaintext)
            
            # 记录日志
            self.log_operation("解密", file_path, "成功")
            
            print(f"文件解密成功: {decrypted_file}")
            return decrypted_file
        except Exception as e:
            self.log_operation("解密", file_path, f"失败: {str(e)}")
            print(f"解密文件时出错: {str(e)}")
            return None

def clear_screen():
    """清空控制台屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """显示主菜单"""
    clear_screen()
    print("=" * 50)
    print("简单文件加密工具")
    print("=" * 50)
    print("1. 加密文件")
    print("2. 解密文件")
    print("3. 退出")
    print("=" * 50)
    choice = input("请选择操作 (1-3): ")
    return choice

def select_file():
    """选择文件"""
    while True:
        file_path = input("请输入文件路径: ").strip()
        if os.path.isfile(file_path):
            return file_path
        else:
            print("文件不存在，请重新输入")

def get_password(action):
    """获取密码"""
    while True:
        password = input(f"请输入用于{action}的密码: ").strip()
        if password:
            confirm = input("请再次输入密码确认: ").strip()
            if password == confirm:
                return password
            else:
                print("两次输入的密码不一致，请重试")
        else:
            print("密码不能为空")

def encrypt():
    encryptor = SimpleFileEncryptor()
    
    while True:
        choice = show_menu()
        
        if choice == '1':  # 加密文件
            clear_screen()
            print("=" * 50)
            print("文件加密")
            print("=" * 50)
            
            # 选择文件
            file_path = select_file()
            
            # 密钥选项
            print("\n[密钥选项]")
            print("1. 创建新密钥")
            print("2. 使用已有密钥")
            key_choice = input("请选择 (1-2): ")
            
            key = None
            password = None
            
            if key_choice == '1':
                # 创建新密钥
                print("\n[创建新密钥]")
                print("1. 使用密码保护")
                print("2. 生成随机密钥")
                key_type = input("请选择 (1-2): ")
                
                if key_type == '1':
                    password = get_password("加密")
                    key = encryptor.generate_key(password)
                    print("\n已创建受密码保护的密钥")
                else:
                    key = encryptor.generate_key()
                    print("\n已生成随机密钥")
            elif key_choice == '2':
                # 使用已有密钥
                print("\n[使用已有密钥]")
                if os.path.exists(encryptor.key_file):
                    print("检测到密钥文件")
                    key_option = input("密钥是否受密码保护? (y/n): ").lower()
                    
                    if key_option == 'y':
                        password = input("请输入密码: ").strip()
                        key = encryptor.load_key(password)
                    else:
                        key = encryptor.load_key()
                    
                    if key:
                        print("密钥加载成功")
                    else:
                        print("无法加载密钥，请重试")
                        continue
                else:
                    print("找不到密钥文件")
                    continue
            
            if key:
                # 执行加密
                encryptor.encrypt_file(file_path, key)
            else:
                print("无法获取有效密钥")
            
            input("\n按Enter键返回主菜单...")
        
        elif choice == '2':  # 解密文件
            clear_screen()
            print("=" * 50)
            print("文件解密")
            print("=" * 50)
            
            # 选择文件
            file_path = select_file()
            
            # 加载密钥
            key = None
            if os.path.exists(encryptor.key_file):
                print("\n检测到密钥文件")
                key_option = input("密钥是否受密码保护? (y/n): ").lower()
                
                if key_option == 'y':
                    password = input("请输入密码: ").strip()
                    key = encryptor.load_key(password)
                else:
                    key = encryptor.load_key()
            else:
                print("\n找不到密钥文件")
                print("请将密钥文件放在同一目录下")
                input("\n按Enter键返回主菜单...")
                continue
            
            if key:
                # 执行解密
                encryptor.decrypt_file(file_path, key)
            else:
                print("无法加载密钥")
            
            input("\n按Enter键返回主菜单...")
        
        elif choice == '3':  # 退出
            print("感谢使用，再见！")
            break
        
        else:
            print("无效选择，请重新输入")
            time.sleep(1)

if __name__ == "__main__":
    encrypt()
