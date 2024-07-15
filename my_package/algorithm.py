def quickSort(arr, left=None, right=None):
    """
    快速排序算法，使用 Hoare 分区方案和三数中位数选择枢轴。

    Args:
        arr: 要排序的列表。
        left: 排序子数组的起始索引。
        right: 排序子数组的结束索引。

    Returns:
        排序后的列表。
    """    
    if left is None:
        left = 0
    if right is None:
        right = len(arr) - 1

    while left < right:
        pivot_index = partition(arr, left, right)
        # 优化：先对较短的一边进行排序，减少递归深度
        if pivot_index - left < right - pivot_index:
            quickSort(arr, left, pivot_index - 1)
            left = pivot_index + 1
        else:
            quickSort(arr, pivot_index + 1, right)
            right = pivot_index - 1

def partition(arr, left, right):
    """
    对列表进行分区，并将枢轴放置在正确的位置。

    Args:
        arr: 要分区的列表。
        left: 分区子数组的起始索引。
        right: 分区子数组的结束索引。

    Returns:
        枢轴的最终位置。
    """    
    # 三数取中法
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

# Example usage:
arr = [10, 7, 8, 9, 1, 5]
quickSort(arr)
print(arr)   # Output should be a sorted array: [1, 5, 7, 8, 9, 10]
