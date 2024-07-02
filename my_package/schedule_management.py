import json
import os
import speech_recognition as sr
import pyttsx3
import datetime
import schedule
import time

class ScheduleManager:
    def __init__(self, filename='schedule.json'):
        self.filename = filename
        self.load_schedule()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # 设置语速
        self.engine.setProperty('voice', 'zh')  # 设置中文语音

    def load_schedule(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.schedule = json.load(file)
        else:
            self.schedule = []

    def save_schedule(self):
        with open(self.filename, 'w') as file:
            json.dump(self.schedule, file, indent=4)

    def add_event(self, date, event):
        self.schedule.append({'date': date, 'event': event})
        self.save_schedule()
        self.speak(f'事件 "{event}" 已添加到 {date}')

    def view_schedule(self):
        if not self.schedule:
            self.speak('没有已安排的事件。')
        else:
            for idx, entry in enumerate(self.schedule, start=1):
                self.speak(f"{idx}. {entry['date']} - {entry['event']}")

    def delete_event(self, index):
        try:
            removed = self.schedule.pop(index - 1)
            self.save_schedule()
            self.speak(f'事件 "{removed["event"]}" 在 {removed["date"]} 已删除。')
        except IndexError:
            self.speak('无效的事件编号。')

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            self.speak("请讲...")
            audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio, language='zh-CN')
        except sr.UnknownValueError:
            self.speak("对不起，我没有听懂。")
            return None
        except sr.RequestError:
            self.speak("对不起，服务不可用。")
            return None
            
    def add_event(self, date, time, event, reminder=None, repeat=None):
        try:
            # 将日期和时间转换为 datetime 对象
            datetime_obj = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            self.schedule.append({'date': datetime_obj.strftime("%Y-%m-%d %H:%M"), 
                                  'event': event, 
                                  'reminder': reminder,
                                  'repeat': repeat})
            self.save_schedule()
            self.speak(f'事件 "{event}" 已添加到 {date} {time}')
            # 添加重复事件到 schedule 库
            if repeat:
                self.schedule_event(datetime_obj, event, repeat)
        except ValueError:
            self.speak("日期或时间格式错误，请重新输入。")
            
    def schedule_event(self, datetime_obj, event, repeat):
        if repeat == '每天':
            schedule.every().day.at(datetime_obj.strftime("%H:%M")).do(lambda: self.speak(f"提醒：{event}"))
        elif repeat == '每周':
            schedule.every().week.at(datetime_obj.strftime("%H:%M")).do(lambda: self.speak(f"提醒：{event}"))
        elif repeat == '每月':
            schedule.every().month.at(datetime_obj.strftime("%H:%M")).do(lambda: self.speak(f"提醒：{event}"))

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(1)     
            
    def view_schedule(self):
        if not self.schedule:
            self.speak('没有已安排的事件。')
        else:
            # 按时间排序
            self.schedule.sort(key=lambda item: datetime.datetime.strptime(item['date'], "%Y-%m-%d %H:%M"))
            for idx, entry in enumerate(self.schedule, start=1):
                self.speak(f"{idx}. {entry['date']} - {entry['event']}")    
                    
    def search_event(self, keyword):
        found = False
        for entry in self.schedule:
            if keyword.lower() in entry['event'].lower() or keyword.lower() in entry['category'].lower():
                self.speak(f"{entry['date']} - {entry['event']}")
                found = True
        if not found:
            self.speak("没有找到匹配的事件。")   
                                                    
def schedule_management():
    manager = ScheduleManager()
    # 启动定时器
    thread = threading.Thread(target=manager.run_scheduler)
    thread.start()
    
    while True:
        manager.speak("日程管理器。请说 '添加'、'查看'、'删除' 或 '退出'。")
        choice = manager.listen()

        if choice is not None:
            if '添加' in choice:
                manager.speak("请输入日期，格式为 YYYY-MM-DD。")
                date = manager.listen()
                if date:
                   manager.speak("请输入时间，格式为 HH:MM。")
                   time = manager.listen()
                   if time:
                       manager.speak("请输入事件描述。")
                       event = manager.listen()
                       if event:
                           manager.speak("是否需要设置重复事件？请输入 '每天'、'每周'、'每月' 或 '不设置'。")
                           repeat = manager.listen()
                           if repeat:
                               manager.add_event(date, time, event, repeat=repeat, category=category)
                           else:
                                manager.add_event(date, time, event, repeat=repeat)
                                
            elif '查看' in choice:
                manager.view_schedule()
            elif '删除' in choice:
                manager.view_schedule()
                manager.speak("请输入要删除的事件编号。")
                index = manager.listen()
                if index and index.isdigit():
                    manager.delete_event(int(index))
            elif '搜索' in choice:
                manager.speak("请输入要搜索的关键字。")
                keyword = manager.listen()
                if keyword:
                    manager.search_event(keyword)     
            elif '退出' in choice:
                manager.speak("再见！")
                break
            else:
                manager.speak("无效的选择，请再试一次。")

if __name__ == "__main__":
    chedule_management()
