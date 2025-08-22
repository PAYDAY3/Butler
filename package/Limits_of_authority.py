import hashlib
import getpass
import time
import json
import os
from package.log_manager import LogManager

logger = LogManager.get_logger(__name__)

# 权限级别定义
PERMISSIONS = {
    "普通用户": 1,
    "受限操作": 2,
    "高级操作": 3,
    "查看配置": 2,
    "高级查看": 3
}

# 操作所需的权限级别定义
OPERATIONS = {
    "查看数据": PERMISSIONS["普通用户"],
    "修改配置": PERMISSIONS["受限操作"],
    "核心操作": PERMISSIONS["高级操作"],
    "写入文件": PERMISSIONS["受限操作"],
    "查看配置": PERMISSIONS["查看配置"]
}

# 用户信息存储（包含用户名、密钥哈希和权限级别）
USERS = {
    "admin": {
        "key_hash": hashlib.sha256("admin_key".encode()).hexdigest(),
        "permission": PERMISSIONS["高级操作"]  # 权限级别3
    },
    "operator": {
        "key_hash": hashlib.sha256("operator_key".encode()).hexdigest(),
        "permission": PERMISSIONS["受限操作"]  # 权限级别2
    }
}

# 权限有效时间（秒）
PERMISSION_VALID_TIME = 30 * 60  # 30分钟

# 用户会话管理
user_sessions = {}

# 文件哈希存储文件
HASH_STORAGE_FILE = "file_hashes.json"

def calculate_file_hash(file_path):
    """计算文件的SHA256哈希值"""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(4096)  # 分块读取文件
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return None
    except Exception as e:
        print(f"计算文件哈希时出错: {e}")
        return None

def save_file_hash(file_path, file_hash):
    """保存文件哈希到存储文件"""
    try:
        # 如果文件不存在，创建空字典
        if not os.path.exists(HASH_STORAGE_FILE):
            with open(HASH_STORAGE_FILE, 'w') as f:
                json.dump({}, f)
        
        # 读取现有哈希
        with open(HASH_STORAGE_FILE, 'r') as f:
            hashes = json.load(f)
        
        # 更新哈希值
        hashes[file_path] = file_hash
        
        # 写回文件
        with open(HASH_STORAGE_FILE, 'w') as f:
            json.dump(hashes, f)
        
        return True
    except Exception as e:
        print(f"保存文件哈希时出错: {e}")
        return False

def get_stored_hash(file_path):
    """从存储中获取文件的哈希值"""
    try:
        if not os.path.exists(HASH_STORAGE_FILE):
            return None
            
        with open(HASH_STORAGE_FILE) as f:
            hashes = json.load(f)
            return hashes.get(file_path)
    except Exception as e:
        print(f"获取存储哈希时出错: {e}")
        return None

def verify_file_integrity(file_path):
    """通过比较文件的散列来验证文件的完整性"""
    current_hash = calculate_file_hash(file_path)
    if current_hash is None:
        return False
        
    stored_hash = get_stored_hash(file_path)
    
    if stored_hash is None:
        print(f"警告: 文件 {file_path} 没有存储的哈希值，首次使用?")
        if save_file_hash(file_path, current_hash):
            print(f"已保存文件 {file_path} 的初始哈希值")
            return True
        return False
    
    if current_hash == stored_hash:
        print("文件完整性验证通过")
        return True
    else:
        print("文件完整性受损!")
        return False

def update_session(username):
    """更新用户会话时间"""
    user_sessions[username] = time.time()

def is_session_valid(username):
    """检查用户会话是否有效"""
    if username not in user_sessions:
        return False
    return (time.time() - user_sessions[username]) < PERMISSION_VALID_TIME

def verify_permission(username, required_permission):
    """验证用户权限"""
    logger.info(f"Verifying permission for user '{username}' for permission level {required_permission}")
    try:
        # 检查用户是否存在
        if username not in USERS:
            logger.warning(f"Permission check for non-existent user '{username}'")
            print("用户不存在")
            return False
        
        # 检查会话是否有效
        if is_session_valid(username):
            logger.info(f"Session is still valid for user '{username}'")
            print("权限仍然有效")
            return True
        
        # 会话无效，需要重新验证
        print("此操作需要权限，请输入密钥：")
        input_key = getpass.getpass("密钥：")
        hashed_key = hashlib.sha256(input_key.encode()).hexdigest()
        
        # 验证密钥
        if USERS[username]["key_hash"] == hashed_key:
            user_permission = USERS[username]["permission"]
            if user_permission >= required_permission:
                update_session(username)  # 更新会话时间
                logger.info(f"Permission granted for user '{username}'")
                print("权限验证成功")
                return True
            else:
                logger.warning(f"Permission denied for user '{username}' - insufficient permission")
                print("权限不足")
                return False
        else:
            logger.warning(f"Permission denied for user '{username}' - invalid key")
            print("密钥无效")
            return False
            
    except KeyError as e:
        logger.error(f"User configuration error: {e}")
        print(f"用户配置错误: {e}")
        return False
    except PermissionError as e:
        logger.error(f"Permission system error: {e}")
        print(f"权限系统错误: {e}")
        return False
    except Exception as e:
        logger.error(f"An error occurred during permission verification: {e}")
        print(f"权限验证过程中出错: {e}")
        return False

# 权限控制装饰器
def require_permission(operation_name):
    def decorator(func):
        def wrapper(username, *args, **kwargs):
            required_permission = OPERATIONS.get(operation_name)
            if required_permission is None:
                print(f"未知操作: {operation_name}")
                return None
                
            if verify_permission(username, required_permission):
                print(f"权限验证成功，正在执行操作：{operation_name}")
                # 记录审计日志
                log_operation(username, operation_name, "执行")
                return func(username, *args, **kwargs)
            else:
                print(f"权限不足，无法执行操作：{operation_name}")
                # 记录审计日志
                log_operation(username, operation_name, "拒绝")
        return wrapper
    return decorator

# 查询操作所需的权限
def get_required_permission(operation):
    return OPERATIONS.get(operation, None)

# 审计日志功能
def log_operation(username, operation, status):
    """记录操作到审计日志"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] 用户: {username}, 操作: {operation}, 状态: {status}\n"
    
    try:
        with open("audit.log", "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"记录审计日志时出错: {e}")

# 操作函数
@require_permission("查看数据")
def view_data(username, file_path):
    if verify_file_integrity(file_path):
        try:
            with open(file_path, 'r') as file:
                data = file.read()
                print(f"文件内容:\n{data}")
                return True
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return False
    else:
        print("文件完整性受损!无法查看数据")
        return False

@require_permission("修改配置")
def modify_config(username):
    print("正在修改配置...")
    # 这里添加实际的配置修改逻辑
    return True

@require_permission("核心操作")
def core_operation(username):
    print("执行核心操作...")
    # 这里添加实际的核心操作逻辑
    return True

# 提供操作列表及其所需权限
def print_operations():
    print("可用操作及其所需权限级别：")
    print("=" * 40)
    for operation, level in OPERATIONS.items():
        # 找到权限级别对应的名称
        permission_name = [key for key, value in PERMISSIONS.items() if value == level]
        if permission_name:
            print(f"- {operation}: {permission_name[0]} (级别 {level})")
        else:
            print(f"- {operation}: 未知权限 (级别 {level})")

# 用户登录功能
def login():
    """用户登录并返回用户名"""
    username = input("用户名: ")
    password = getpass.getpass("密码: ")
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    if username in USERS and USERS[username]["key_hash"] == hashed_pw:
        update_session(username)
        logger.info(f"User '{username}' logged in successfully")
        print(f"登录成功! 欢迎 {username}")
        return username
    else:
        logger.warning(f"Failed login attempt for username '{username}'")
        print("登录失败: 用户名或密码错误")
        return None

# 主程序
def run():
    logger.info("Limits of authority tool started")
    main()

def main():
    logger.info("Limits of authority main function started")
    print("=== 权限控制系统 ===")
    
    # 初始化文件哈希存储
    if not os.path.exists(HASH_STORAGE_FILE):
        with open(HASH_STORAGE_FILE, 'w') as f:
            json.dump({}, f)
    
    # 用户登录
    current_user = login()
    if not current_user:
        return
    
    while True:
        print("\n请选择操作:")
        print("1. 查看操作列表")
        print("2. 查看文件内容")
        print("3. 修改配置")
        print("4. 执行核心操作")
        print("5. 退出系统")
        
        choice = input("> ")
        
        if choice == "1":
            print_operations()
        elif choice == "2":
            file_path = input("请输入文件路径: ")
            view_data(current_user, file_path)
        elif choice == "3":
            modify_config(current_user)
        elif choice == "4":
            core_operation(current_user)
        elif choice == "5":
            print("退出系统...")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
