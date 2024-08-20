from typing import List, Tuple
import importlib

def read_file_list(file_path: str) -> List[Tuple[str, int, str]]:
    """读取文件列表，并获取每个文件的优先级、插入位置标识符。"""
    with open(file_path, 'r') as file:
        return [(line.split()[0], int(line.split()[1]), line.split()[2]) for line in file if line.strip()]

def hybridSort(arr: List[Tuple[str, int, str]], left=None, right=None, depth=0):
    """
    混合排序算法，结合快速排序和插入排序。

    Args:
        arr: 要排序的列表。
        left: 排序子数组的起始索引。
        right: 排序子数组的结束索引。
        depth: 递归深度（用于调试输出缩进）。

    Returns:
        排序后的列表。
    """
    if left is None:
        left = 0
    if right is None:
        right = len(arr) - 1

    # 插入排序优化: 对于小数组使用插入排序
    if right - left < 10:
        insertionSort(arr, left, right)
        return

    if left < right:
        pivot_index = partition(arr, left, right, depth)
        # 优化：先对较短的一边进行排序，减少递归深度
        if pivot_index - left < right - pivot_index:
            hybridSort(arr, left, pivot_index - 1, depth + 1)
            hybridSort(arr, pivot_index + 1, right, depth + 1)
        else:
            hybridSort(arr, pivot_index + 1, right, depth + 1)
            hybridSort(arr, left, pivot_index - 1, depth + 1)

def partition(arr: List[Tuple[str, int, str]], left: int, right: int, depth: int) -> int:
    """
    对列表进行分区，并将枢轴放置在正确的位置。

    Args:
        arr: 要分区的列表。
        left: 分区子数组的起始索引。
        right: 分区子数组的结束索引。
        depth: 递归深度（用于调试输出缩进）。

    Returns:
        枢轴的最终位置。
    """
    mid = (left + right) // 2
    pivot = median_of_three(arr, left, mid, right)
    arr[left], arr[pivot] = arr[pivot], arr[left]
    pivot = left

    i = left + 1
    j = right
    while True:
        while i <= j and arr[i] < arr[pivot]:
            i += 1
        while i <= j and arr[j] >= arr[pivot]:
            j -= 1
        if i <= j:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
            j -= 1
        else:
            break
    arr[pivot], arr[j] = arr[j], arr[pivot]
    return j

def median_of_three(arr: List[Tuple[str, int, str]], left: int, mid: int, right: int) -> int:
    """
    返回三个元素的中位数的索引。

    Args:
        arr: 包含三个元素的列表。
        left: 列表中第一个元素的索引。
        mid: 列表中第二个元素的索引。
        right: 列表中第三个元素的索引。

    Returns:
        三个元素中位数的索引。
    """
    if arr[left][1] < arr[mid][1]:
        if arr[mid][1] < arr[right][1]:
            return mid
        elif arr[left][1] < arr[right][1]:
            return right
        else:
            return left
    else:
        if arr[left][1] < arr[right][1]:
            return left
        elif arr[mid][1] < arr[right][1]:
            return right
        else:
            return mid

def insertionSort(arr: List[Tuple[str, int, str]], left: int, right: int):
    """
    插入排序算法，对小数组进行排序。

    Args:
        arr: 要排序的列表。
        left: 排序子数组的起始索引。
        right: 排序子数组的结束索引。
    """
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        
def execute_program(module_name: str, modules: List[Tuple[str, int, str]], position_mapping: dict):
    """执行指定模块，并在适当位置插入和执行其他模块。"""
    print(f"正在执行模块: {module_name}")
    try:
        module = importlib.import_module(module_name)
        module.run()  # 假设模块中有一个名为 run 的函数
    except ImportError as error:
        print(f"导入模块失败: {error}")
    except AttributeError:
        print(f"模块中未找到运行函数: {module_name}")

    # 执行后检查是否有其他模块插入到该模块后
    for mod, _, position_key in modules:
        if position_key == module_name:  # 如果模块的插入点是当前模块
            target_file, placeholder = position_mapping.get(position_key, (None, None))
            if target_file and placeholder:
                insert_content = f"# 插入模块: {mod}\nimport {mod}\n"
                insert_into_file(target_file, insert_content, placeholder)
                execute_program(mod, modules, position_mapping)  # 递归执行插入的模块

def insert_into_file(file_path: str, insert_content: str, after_marker: str):
    """将内容插入到指定文件的指定标记之后。"""
    with open(file_path, 'r') as file:
        content = file.read()

    insert_point = content.find(after_marker)
    if insert_point == -1:
        raise ValueError(f"未找到插入标记: {after_marker}")

    insert_index = insert_point + len(after_marker)

    new_content = content[:insert_index] + "\n" + insert_content + "\n" + content[insert_index:]

    with open(file_path, 'w') as file:
        file.write(new_content)

if __name__ == "__main__":
    # 读取模块优先级列表
    file_list_path = "file_list.txt"
    
    # 读取文件列表（包括优先级）
    files_with_priority = read_file_list(file_list_path)

    # 将优先级转换为整数
    files_with_priority = [(f, int(p)) for f, p in files_with_priority]

    # 使用混合排序算法排序文件列表（按优先级排序）
    hybridSort(files_with_priority)

    # 将排序后的列表写入新文件
    write_sorted_list(sorted_list_path, files_with_priority)

    # 创建 Handler 实例
    handler = Handler(program_folder="programs")  # 假设所有的程序模块都在 programs 目录下
    
    # 插入位置映射表：映射位置标识符到文件和占位符
    position_mapping = {
        "module1": ("main.py", "#PLACEHOLDER_1"),
        "module2": ("utils.py", "#PLACEHOLDER_2"),
        "module3": ("config.py", "#PLACEHOLDER_3")
    }
    
    # 执行排序后的程序文件
    for module_name, _, _ in files_with_priority:
        execute_program(module_name, files_with_priority, position_mapping)
