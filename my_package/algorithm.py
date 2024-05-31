def quickSort(arr, left=None, right=None):
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
