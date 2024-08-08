
def hybridSort(arr, left=None, right=None, depth=0):
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

def partition(arr, left, right, depth):
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

def median_of_three(arr, left, mid, right):
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
    if arr[left] < arr[mid]:
        if arr[mid] < arr[right]:
            return mid
        elif arr[left] < arr[right]:
            return right
        else:
            return left
    else:
        if arr[left] < arr[right]:
            return left
        elif arr[mid] < arr[right]:
            return right
        else:
            return mid

def insertionSort(arr, left, right):
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
        
def read_file_list(file_path):
    with open(file_path, 'r') as file:
        return [tuple(line.strip().split()) for line in file if line.strip()]

def write_sorted_list(file_path, sorted_list):
    with open(file_path, 'w') as file:
        for item in sorted_list:
            file.write(f"{item[0]} {item[1]}\n")

if __name__ == "__main__":
    file_list_path = "file_list.txt"
    sorted_list_path = "sorted_file_list.txt"

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

    # 执行排序后的程序文件
    for file_name, _ in files_with_priority:
        execute_program(file_name, handler)
