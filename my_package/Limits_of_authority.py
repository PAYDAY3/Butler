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

# 查询操作所需的权限
def get_required_permission(operation):
    return OPERATIONS.get(operation, None)

# 操作函数
def view_data():
    print("正在查看数据...")

def modify_config():
    required_permission = get_required_permission("修改配置")
    if required_permission and verify_permission(required_permission):
        print("正在修改配置...")
    else:
        print("操作被拒绝：权限不足")

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

# 示例主程序
def main():
    print_operations()
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ["退出", "结束"]:
            break
        elif user_input.lower() == "查看数据":
            view_data()
        elif user_input.lower() == "修改配置":
            modify_config()
        elif user_input.lower() == "核心操作":
            core_operation()
        else:
            print("未知命令")

if __name__ == "__main__":
    main()
