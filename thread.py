import threading
import time
import queue
import subprocess

class MyThread(threading.Thread):
    def __init__(self, thread_id, name, counter, shared_queue):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.shared_queue = shared_queue
    
    def run(self):
        print("开始线程：" + self.name)
        print("线程 %s 正在执行任务..." % self.name)
        
        try:
            for i in range(10):
                time.sleep(1)
                print_progress(i+1, 10, prefix='Progress:', suffix='Complete', bar_length=50)
            
            self.shared_queue.put("%s 执行完毕" % self.name)
            
        except Exception as e:
            print("线程 %s 发生异常：%s" % (self.name, str(e)))
        
        finally:
            print("退出线程：" + self.name)

def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = fill * filled_length + '-' * (bar_length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    
    if iteration == total:
        print()

def start_external_python_script(script_name):
    process = subprocess.Popen(['python', script_name])
    process.wait()
    print('外部Python脚本退出状态', process.returncode)

def start_threads():
    exitFlag = 0
    shared_queue = queue.Queue()
    threads = []

    try:
        for i in range(10):
            thread = MyThread(i+1, "Thread-"+str(i+1), i+1, shared_queue)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        while not shared_queue.empty():
            item = shared_queue.get()
            print(item)
    except Exception as e:
        print("程序出错了：", e)

    print("退出主线程")

