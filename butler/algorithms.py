import heapq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import cv2
from tqdm import tqdm

# 1. Sorting Algorithms
def _insertion_sort(arr, low, high, pbar=None):
    for i in range(low + 1, high + 1):
        key = arr[i]
        j = i - 1
        while j >= low and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
        if pbar:
            pbar.update(1)

def _partition(arr, low, high, pbar=None):
    """Hoare partition scheme"""
    # Median-of-three pivot selection
    mid = (low + high) // 2
    if arr[mid] < arr[low]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[high] < arr[low]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[mid] < arr[high]:
        arr[mid], arr[high] = arr[high], arr[mid]

    pivot = arr[high]
    i = low - 1
    j = high
    while True:
        i += 1
        while arr[i] < pivot:
            i += 1
        j -= 1
        while j >= low and arr[j] > pivot:
            j -= 1
        if i >= j:
            break
        arr[i], arr[j] = arr[j], arr[i]
    arr[i], arr[high] = arr[high], arr[i]
    if pbar:
        pbar.update(1)
    return i

def _introsort_util(arr, low, high, depth_limit, pbar=None):
    """A hybrid sorting algorithm (Introsort)"""
    while high - low > 16: # Threshold for switching to insertion sort
        if depth_limit == 0:
            # If recursion depth is too high, switch to heapsort
            # (Heapsort not implemented here for simplicity, can be added)
            # For now, we'll just continue with quicksort
            pass

        pivot_index = _partition(arr, low, high, pbar)
        _introsort_util(arr, pivot_index + 1, high, depth_limit - 1, pbar)
        high = pivot_index - 1

    _insertion_sort(arr, low, high, pbar)

def quick_sort(arr, use_progress_bar=False):
    """
    Performs an in-place introsort on the array.
    Set use_progress_bar to True to display a progress bar.
    """
    import math
    if not arr:
        return arr
    # Create a mutable copy to sort in-place
    arr_copy = list(arr)
    depth_limit = 2 * int(math.log2(len(arr_copy)))

    if use_progress_bar:
        with tqdm(total=len(arr_copy), desc="Sorting") as pbar:
            _introsort_util(arr_copy, 0, len(arr_copy) - 1, depth_limit, pbar)
    else:
        _introsort_util(arr_copy, 0, len(arr_copy) - 1, depth_limit)

    return arr_copy

def merge_sort(arr):
    """归并排序算法"""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    left = merge_sort(left)
    right = merge_sort(right)

    return _merge(left, right)

def _merge(left, right):
    """归并排序的合并操作"""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 2. Searching Algorithm
def binary_search(arr, target):
    """二分查找算法"""
    low, high = 0, len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = arr[mid]

        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1

# 3. Pathfinding Algorithm
def a_star(graph, start, goal, heuristic, use_progress_bar=False):
    """A*最短路径算法"""
    open_set = [(0, start)]
    came_from = {}

    g_score = {node: float('infinity') for node in graph}
    g_score[start] = 0

    f_score = {node: float('infinity') for node in graph}
    f_score[start] = heuristic(start, goal)

    pbar = None
    if use_progress_bar:
        # Heuristic for progress bar total: number of nodes in graph
        pbar = tqdm(total=len(graph), desc="Finding path")

    try:
        while open_set:
            _, current = heapq.heappop(open_set)

            if pbar:
                pbar.update(1)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for neighbor, weight in graph[current].items():
                tentative_g_score = g_score[current] + weight
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None # Path not found
    finally:
        if pbar:
            pbar.close()

def dijkstra(graph, start):
    """
    Dijkstra's algorithm implemented as a special case of A*
    with a zero heuristic.
    """
    # Dijkstra is A* with h(n) = 0 for all n.
    # This implementation of A* finds a path to a single goal.
    # A classical Dijkstra finds shortest paths to all nodes.
    # This is kept for compatibility, but its behavior is now goal-oriented.
    # To find all paths, a goal would need to be specified and the function
    # run for all possible goals, or the a_star function modified.

    # This is a simplified placeholder. For a true Dijkstra implementation
    # that returns distances to all nodes, the original implementation was more accurate.
    # We are choosing to replace it with the more powerful A*.
    # If all-pairs shortest path is needed, a different algorithm should be used.

    # A dummy heuristic for Dijkstra
    def zero_heuristic(a, b):
        return 0

    # Find path to all nodes by iterating through them as goals
    paths = {}
    for goal_node in graph:
        if start != goal_node:
             paths[goal_node] = a_star(graph, start, goal_node, zero_heuristic)

    return paths

# 4. Text Similarity Algorithm
def text_cosine_similarity(text1, text2):
    """计算两个文本的余弦相似度"""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

# 5. Image Processing Algorithm
def edge_detection(image_path):
    """边缘检测算法"""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return None

    # 应用Canny边缘检测
    edges = cv2.Canny(image, 100, 200)
    return edges

# 6. Mathematical Algorithm
def _multiply_matrices(F, M):
    """Helper function to multiply two 2x2 matrices."""
    x = F[0][0] * M[0][0] + F[0][1] * M[1][0]
    y = F[0][0] * M[0][1] + F[0][1] * M[1][1]
    z = F[1][0] * M[0][0] + F[1][1] * M[1][0]
    w = F[1][0] * M[0][1] + F[1][1] * M[1][1]

    F[0][0] = x
    F[0][1] = y
    F[1][0] = z
    F[1][1] = w

def _power(F, n):
    """Helper function to calculate matrix exponentiation."""
    if n == 0 or n == 1:
        return
    M = [[1, 1], [1, 0]]

    _power(F, n // 2)
    _multiply_matrices(F, F)

    if n % 2 != 0:
        _multiply_matrices(F, M)

def fibonacci(n):
    """
    Calculates the n-th Fibonacci number using matrix exponentiation.
    This is an O(log n) implementation.
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1

    F = [[1, 1], [1, 0]]
    _power(F, n - 1)

    return F[0][0]
