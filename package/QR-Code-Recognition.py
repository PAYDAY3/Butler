import cv2
import requests
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
import time

# Set default save folder path
DEFAULT_SAVE_FOLDER = "./my_package/downloaded"
if not os.path.exists(DEFAULT_SAVE_FOLDER):
    os.makedirs(DEFAULT_SAVE_FOLDER)

def select_save_folder(default_save_folder):
    folder = filedialog.askdirectory(initialdir=default_save_folder, title="选择保存文件夹")
    return folder if folder else default_save_folder

def download_file(url, save_folder):
    local_filename = os.path.join(save_folder, url.split('/')[-1])
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"文件已下载: {local_filename}")
    except requests.RequestException as e:
        print(f"下载文件时出错: {e}")

def confirm_action(action, url, save_folder):
    root = tk.Tk()
    root.withdraw()

    if action == "download":
        result = messagebox.askyesno("下载确认", f"您想从以下链接下载文件吗？\n{url}?")
        if result:
            download_file(url, save_folder)
    elif action == "open":
        result = messagebox.askyesno("打开 URL 确认", f"您想打开以下网址吗？\n{url}?")
        if result:
            import webbrowser
            webbrowser.open(url)

    root.destroy()

def scan_qr_code(save_folder):
    cap = cv2.VideoCapture(0)

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

                if data.startswith('http://') or data.startswith('https://'):
                    print(f"检测到的 URL: {data}")
                    Thread(target=confirm_action, args=("download", data, save_folder)).start()
                    break

        cv2.imshow('二维码扫描器', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)  # Add a small delay to reduce CPU usage

    cap.release()
    cv2.destroyAllWindows()

def on_exit(root):
    if messagebox.askokcancel("退出确认", "您确定要退出吗？"):
        root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("二维码扫描器")

    save_folder = select_save_folder(DEFAULT_SAVE_FOLDER)
    print("正在扫描二维码... 按 'q' 退出。")
    Thread(target=scan_qr_code, args=(save_folder,)).start()

    root.protocol("WM_DELETE_WINDOW", lambda: on_exit(root))
    root.mainloop()
