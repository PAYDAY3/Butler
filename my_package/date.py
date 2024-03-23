import datetime

def date():
    day = int(datetime.datetime.now().day)
    month = int(datetime.datetime.now().month)
    year = int(datetime.datetime.now().year)
    print(f"当前日期为{year}年{month}月{day}日")

if __name__ == "__main__":
    date()