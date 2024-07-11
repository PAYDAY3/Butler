import time
import datetime
import subprocess

class ScheduledTask:
    def __init__(self, task_name, task_function, schedule_type, schedule_value):
        """
        初始化定时任务对象

        Args:
            task_name (str): 任务名称
            task_function (function): 要执行的任务函数
            schedule_type (str): 定时类型，可选值：'second', 'minute', 'hour', 'day', 'month', 'year'
            schedule_value (int): 定时值，例如：'second'=10，表示每10秒执行一次
        """
        self.task_name = task_name
        self.task_function = task_function
        self.schedule_type = schedule_type
        self.schedule_value = schedule_value
        self.last_run_time = None
        
    def _load_last_run_time(self):
        """从文件加载上次运行时间"""
        try:
            with open(f"{self.task_name}_last_run.txt", "r") as f:
                last_run_str = f.read().strip()
                return datetime.datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%S.%f")
        except FileNotFoundError:
            return None

    def _save_last_run_time(self):
        """将上次运行时间保存到文件"""
        with open(f"{self.task_name}_last_run.txt", "w") as f:
            f.write(self.last_run_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
    def get_next_run_time(self):
        """计算下次运行时间"""
        now = datetime.datetime.now()
        if self.last_run_time is None:
            self.last_run_time = now
            return now

        if self.schedule_type == 'second':
            next_run_time = self.last_run_time + datetime.timedelta(seconds=self.schedule_value)
        elif self.schedule_type == 'minute':
            next_run_time = self.last_run_time + datetime.timedelta(minutes=self.schedule_value)
        elif self.schedule_type == 'hour':
            next_run_time = self.last_run_time + datetime.timedelta(hours=self.schedule_value)
        elif self.schedule_type == 'day':
            next_run_time = self.last_run_time + datetime.timedelta(days=self.schedule_value)
        elif self.schedule_type == 'month':
            next_run_time = self.last_run_time + datetime.timedelta(days=30*self.schedule_value)  # 近似每月30天
        elif self.schedule_type == 'year':
            next_run_time = self.last_run_time + datetime.timedelta(days=365*self.schedule_value)  # 近似每年365天
        else:
            raise ValueError(f"Invalid schedule type: {self.schedule_type}")

        if next_run_time < now:  # 如果下次运行时间小于当前时间，则更新为下一个时间段
            next_run_time = self.get_next_run_time()

        return next_run_time

    def run(self):
        """执行任务"""
        try:
            # 使用 subprocess.run 执行命令
            process = subprocess.run(self.task_command.split(), check=True, capture_output=True, text=True)
            self.last_run_time = datetime.datetime.now()
            self._save_last_run_time()
            self._write_log(f"任务 {self.task_name} 执行成功，当前时间：{datetime.datetime.now()}，输出：{process.stdout}")
        except subprocess.CalledProcessError as e:
            self._write_log(f"任务 {self.task_name} 执行失败，错误代码：{e.returncode}，错误信息：{e.stderr}")
        except Exception as e:
            self._write_log(f"任务 {self.task_name} 执行失败：{e}")

    def _write_log(self, message):
        """写入日志文件"""
        with open("scheduled_tasks.log", "a") as f:
            f.write(f"{datetime.datetime.now()} - {message}\n")

def main():
    # 定义多个任务
    tasks = [
        ScheduledTask(task_name='任务1', task_command=['python', 'task1.py'], schedule_type='minute', schedule_value=2),  # 每2分钟执行一次
        ScheduledTask(task_name='任务2', task_command=['python', 'task2.py'], schedule_type='hour', schedule_value=6),  # 每6小时执行一次
        ScheduledTask(task_name='任务3', task_command=['python', 'task3.py'], schedule_type='day', schedule_value=1),  # 每天执行一次
    ]

    while True:
        # 获取每个任务的下次运行时间
        next_run_times = [task.get_next_run_time() for task in tasks]

        # 找出下次运行时间最早的任务
        min_index = next_run_times.index(min(next_run_times))
        next_run_time = next_run_times[min_index]

        # 等待到下次运行时间
        time.sleep((next_run_time - datetime.datetime.now()).total_seconds())

        # 执行下次运行时间最早的任务
        tasks[min_index].run()

if __name__ == '__main__':
    main()
