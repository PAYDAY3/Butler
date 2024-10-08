from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
from jarvis import InputProcessor

def generate_key():
    """
    生成16字节的随机密钥。
    """
    return get_random_bytes(16)

def encrypt_file(file_path, key):
    """
    使用AES加密指定文件。
    
    :param file_path: 文件路径
    :param key: 密钥
    """
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    ciphertext = iv + cipher.encrypt(pad(data, AES.block_size))
    
    with open(file_path + '.enc', 'wb') as f:
        f.write(ciphertext)

def decrypt_file(file_path, key):
    """
    使用AES解密指定文件。
    
    :param file_path: 文件路径
    :param key: 密钥
    """
    with open(file_path, 'rb') as f:
        ciphertext = f.read()
    
    iv = ciphertext[:AES.block_size]
    ciphertext = ciphertext[AES.block_size:]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    with open(file_path.replace('.enc', '.dec'), 'wb') as f:
        f.write(plaintext)

def process_directory(directory, key, encrypt=True):
    """
    加密或解密指定目录及子目录中的所有文件。   
    :param directory: 目录路径
    :param key: 密钥
    :param encrypt: True 表示加密，False 表示解密
    """
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if encrypt:
                    encrypt_file(file_path, key)
                else:
                    decrypt_file(file_path, key)

        print(f"目录 '{directory}' 已进行加密或解密处理")
    except Exception as e:
        print(f"处理目录 '{directory}' 时发生错误：{e}")

if __name__ == "__main__":
    input_processor = InputProcessor.InputProcessor()
    key = generate_key()
    print(f"生成的密钥: {key.hex()}")

    path_to_process = input_processor.process_text_input()  # 替换为您的文件或目录路径
    
    if os.path.isdir(path_to_process):
        # 处理整个目录
        process_directory(path_to_process, key, encrypt=True)
        print(f"目录 '{path_to_process}' 已进行加密处理.")
    else:
        # 处理单个文件
        encrypt_file(path_to_process, key)
        print(f"文件 '{path_to_process}' 已经加密")
    
    # 解密
    if os.path.isdir(path_to_process):
        # 处理整个目录
        process_directory(path_to_process, key, encrypt=False)
        print(f"目录 '{path_to_process}' 已被处理以进行解密")
    else:
        # 处理单个文件
        encrypted_file = path_to_process + '.enc'
        decrypt_file(encrypted_file, key)
        print(f"文件 '{encrypted_file}' 已被解密.")
