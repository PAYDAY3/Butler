import threading
import queue
import logging
from concurrent.futures import ThreadPoolExecutor

# 模拟处理任务的函数
def do_something(task):
    return task.upper()

# 获取大任务列表
def get_tasks():
    return ["task1", "task2", "task3", "task4", "task5", "task6", "task7", "task8", "task9", "task10"]

# 定义任务处理函数
def process_task(task, result_queue):
    try:
        task_result = do_something(task)
        result_queue.put(task_result)  # 将处理结果放入队列中
    except Exception as e:
        logging.error(f"处理任务 {task} 时发生错误: {e}")

# 工作线程函数
def worker(subtasks, result_queue):
    results = []
    for task in subtasks:
        task_result = process_task(task, result_queue)
        results.append(task_result)
    return result_queue

# 定义任务分发函数
def dispatch_tasks(tasks, num_threads):
    # 将大任务分解成多个小任务
    subtasks = divide_tasks(tasks, num_threads)

    # 创建线程池
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 将任务提交给线程池执行
        future_to_task = {executor.submit(worker, subtasks[i], queue.Queue()): i for i in range(num_threads)}
        # 等待所有任务完成并获取结果
        results = []
        for future in concurrent.futures.as_completed(future_to_task):
            result_queue = future.result()
            while not result_queue.empty():
                results.extend(result_queue.get())

    return results

# 定义任务分解函数
def divide_tasks(tasks, num_threads):
    # 将大任务分解成多个小任务
    subtasks = []
    for i in range(0, len(tasks), num_threads):
        subtasks.append(tasks[i:i+num_threads])
    return subtasks

   #    
def dispatch_tasks(tasks, num_threads):
    if len(tasks) < 10:  # threshold for small tasks
        return dispatch_tasks_small(tasks, num_threads)
    else:
        return dispatch_tasks_large(tasks, num_threads)

def dispatch_tasks_small(tasks, num_threads):
    # use individual threads for small tasks
    results = []
    for task in tasks:
        result_queue = queue.Queue()
        thread = threading.Thread(target=process_task, args=(task, result_queue))
        thread.start()
        thread.join()
        results.extend(result_queue.get())
    return results

def dispatch_tasks_large(tasks, num_threads):
    # use ThreadPoolExecutor for large tasks
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_task = {executor.submit(worker, subtasks[i], queue.Queue()): i for i in range(num_threads)}
        results = []
        for future in concurrent.futures.as_completed(future_to_task):
            result_queue = future.result()
            while not result_queue.empty():
                results.extend(result_queue.get())
    return results
    #
# 主函数
def process_tasks():
    # 定义大任务，比如需要处理100个任务
    tasks = get_tasks()

    # 定义线程数，根据CPU核心数动态设置
    num_threads = min(len(tasks), os.cpu_count() or 1)

    # 分发任务并等待结果
    result = dispatch_tasks(tasks, num_threads)
    print(result)

if __name__ == "__main__":
    process_tasks()
