import os
import shutil
import sys
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from argparse import ArgumentParser

VALIDATION_STRING = b'MyEncryptionValidation'

def encrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
    try:
        if not out_filename:
            out_filename = in_filename + '.enc'

        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(filesize.to_bytes(8, byteorder='big'))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - len(chunk) % 16)

                    outfile.write(cipher.encrypt(chunk))

                # 添加验证字符串
                outfile.write(VALIDATION_STRING)

    except Exception as e:
        print(f"加密过程中发生错误: {e}")

def decrypt_file(key, in_filename, out_filename=None, chunksize=24 * 1024):
    try:
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            orig_size = int.from_bytes(infile.read(8), byteorder='big')
            iv = infile.read(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0           
                        break

                    outfile.write(cipher.decrypt(chunk))

                outfile.truncate(orig_size)

        # 从加密的中读取验证字符串
        with open(in_filename, 'rb') as infile:
            infile.seek(-len(VALIDATION_STRING), os.SEEK_END)
            validation = infile.read()
            if validation != VALIDATION_STRING:
                raise ValueError('无效的加密文件')

    except Exception as e:
        print(f"解密过程中发生错误: {e}")

def encrypt_files(key, file_paths):
    for file_path in file_paths:
        out_file_path = file_path + '.enc'
        encrypt_file(key, file_path, out_file_path)

def decrypt_files(key, file_paths):
    for file_path in file_paths:
        out_file_path = os.path.splitext(file_path)[0]
        decrypt_file(key, file_path, out_file_path)

def collect_files_in_directory(directory):
    file_paths = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths

def encipher():
    parser = argparse.ArgumentParser(description="Encrypt or decrypt files.")
    parser.add_argument('action', choices=['encrypt', 'decrypt'], help="Action to perform: 'encrypt' or 'decrypt'")
    parser.add_argument('key', type=str, help="Encryption key")
    parser.add_argument('paths', nargs='+', help="File or directory paths to process")

    args = parser.parse_args()
    key = args.key.encode()  
    if len(key) not in [16, 24, 32]:
        sys.exit(1)
        
    file_paths = []
    for path in args.paths:
        if os.path.isdir(path):
            file_paths.extend(collect_files_in_directory(path))
        else:
            file_paths.append(path)
    if args.action == 'encrypt':
        encrypt_files(key, file_paths)
    elif args.action == 'decrypt':
        decrypt_files(key, file_paths)

if __name__ == '__main__':
    encipher()

#要加密文件或目录，可以运行：
python encrypt_decrypt.py encrypt mysecretkey /path/to/file1 /path/to/file2


#要解密文件或目录，可以运行：
python encrypt_decrypt.py decrypt mysecretkey /path/to/file1.enc /path/to/file2.enc
