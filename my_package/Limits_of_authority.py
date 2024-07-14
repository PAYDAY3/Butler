import hashlib
import getpass
import time

# 权限级别定义
PERMISSIONS = {
    "普通用户": 1,
    "受限操作": 2,
    "高级操作": 3
}

# 操作所需的权限级别定义
OPERATIONS = {
    "查看数据": PERMISSIONS["普通用户"],
    "修改配置": PERMISSIONS["受限操作"],
    "核心操作": PERMISSIONS["高级操作"],
    "写入文件": PERMISSIONS["受限操作"]
}

# 权限密钥存储（实际应使用更安全的存储方式）
USER_KEYS = {
    "admin": hashlib.sha256("admin_key".encode()).hexdigest(),  # 示例密钥
}

# 权限有效时间（秒）
PERMISSION_VALID_TIME = 30 * 60  # 30分钟

# 记录上次验证时间
last_verified_time = None
def calculate_file_hash(file_path):
    """Calculates the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(4096)  # 分块读取文件
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()
    
def verify_file_integrity(file_path):
    """通过比较文件的散列来验证文件的完整性"""
    current_hash = calculate_file_hash(file_path)
    stored_hash = get_stored_hash(file_path)  # 函数从存储中检索哈希值
    if current_hash == stored_hash:
        print("文件完整性验证")
        return True
    else:
        print("文件完整性受损!")
        return False
        
# 获取并验证权限密钥
def verify_permission(required_permission):
    global last_verified_time
    
    # 检查权限是否仍然有效
    if last_verified_time and (time.time() - last_verified_time < PERMISSION_VALID_TIME):
        print("权限仍然有效")
        return True
    
    print("此操作需要权限，请输入密钥：")
    input_key = getpass.getpass("密钥：")
    hashed_key = hashlib.sha256(input_key.encode()).hexdigest()
    
    for user, key in USER_KEYS.items():
        if key == hashed_key:
            user_permission = PERMISSIONS["高级操作"]  # 假设已验证用户为高级操作权限
            if user_permission >= required_permission:
                last_verified_time = time.time()  # 记录当前时间
                print("权限验证成功")
                return True
            else:
                print("权限不足")
                return False
    print("密钥无效")
    return False
    
# 权限控制装饰器
def require_permission(operation_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            required_permission = OPERATIONS.get(operation_name)
            if required_permission and verify_permission(required_permission):
                print(f"权限验证成功，正在执行操作：{operation_name}")
                return func(*args, **kwargs)
            else:
                print(f"权限不足，无法执行操作：{operation_name}")
        return wrapper
    return decorator
    
# 查询操作所需的权限
def get_required_permission(operation):
    return OPERATIONS.get(operation, None)

# 操作函数
@require_permission("查看数据")
def view_data(file_path):
    if verify_file_integrity(file_path):
        # 从文件中读取和显示数据
        with open(file_path, 'r') as file:
            data = file.read()
            print(data)
    else:
        print("文件完整性受损!无法查看数据")

@require_permission("修改配置")
def modify_config():
    required_permission = get_required_permission("修改配置")
    if required_permission and verify_permission(required_permission):
        print("正在修改配置...")
    else:
        print("操作被拒绝：权限不足")
        
@require_permission("核心操作")
def core_operation():
    required_permission = get_required_permission("核心操作")
    if required_permission and verify_permission(required_permission):
        print("执行核心操作...")
    else:
        print("操作被拒绝：权限不足")

# 提供操作列表及其所需权限
def print_operations():
    print("可用操作及其所需权限级别：")
    for operation, level in OPERATIONS.items():
        permission_level = [key for key, value in PERMISSIONS.items() if value == level][0]
        print(f"- {operation}: {permission_level}")
