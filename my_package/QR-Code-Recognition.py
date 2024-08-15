import cv2
import requests
import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

save_folder = "./my_package/downloaded"  # 在此处替换为您希望保存文件的文件夹路径
if not os.path.exists(save_folder):
    os.makedirs(save_folder)  # 如果文件夹不存在，则创建它
        
def download_file(url, save_folder):
    local_filename = os.path.join(save_folder, url.split('/')[-1])  # 结合文件夹路径和文件名
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # 检查请求是否成功
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print(f"文件已下载: {local_filename}")
    except Exception as e:
        print(f"下载文件时出错: {e}")

def confirm_action(action, url, save_folder):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    if action == "download":
        result = messagebox.askyesno("下载确认", f"您想从以下链接下载文件吗？\n{url}?")
        if result:
            download_file(url, save_folder)  # 将保存文件夹路径传给download_file
    elif action == "open":
        result = messagebox.askyesno("打开 URL 确认", f"您想打开以下网址吗？\n{url}?")
        if result:
            import webbrowser
            webbrowser.open(url)

    root.destroy()  

def scan_qr_code(save_folder):
    cap = cv2.VideoCapture(0)  # 初始化网络摄像头

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(frame)
        if bbox is not None:
            for i in range(len(bbox)):
                cv2.line(frame, tuple(bbox[i][0]), tuple(bbox[(i + 1) % 4][0]), (255, 0, 0), 3)

            if data:
                cv2.putText(frame, data, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # 检查检测到的数据是否为 URL
                if data.startswith('http://') or data.startswith('https://'):
                    print(f"检测到的 URL: {data}")
                    
                    # 启动一个线程来处理用户确认，这样不会阻塞视频流
                    Thread(target=confirm_action, args=("download", data, save_folder)).start()
                    break  # 找到并处理后退出

        cv2.imshow('二维码扫描器', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("正在扫描二维码... 按 'q' 退出。")
    scan_qr_code(save_folder)
