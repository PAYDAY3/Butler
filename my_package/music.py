import pygame
import os
import json
from my_package.takecommand import takecommand

# 初始化pygame
pygame.mixer.init()

# 音乐库文件路径
MUSIC_LIBRARY_FILE = "music_library.json"

# 音乐播放器函数
def music_player():
    music_library = []

    # 从文件中加载音乐库
    def load_music_library():
        try:
            with open(MUSIC_LIBRARY_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    # 保存音乐库到文件
    def save_music_library():
        with open(MUSIC_LIBRARY_FILE, "w") as f:
            json.dump(music_library, f)

    # 遍历整个文件系统以查找音乐文件
    def build_music_library():
        for root, _, files in os.walk("/"):
            for file in files:
                if file.endswith(('.mp3', '.wav', '.ogg')):
                    music_library.append(os.path.join(root, file))

    # 加载音乐库，如果文件不存在则构建
    music_library = load_music_library()
    if not music_library:
        print("正在构建音乐库，这可能需要一些时间...")
        build_music_library()
        save_music_library()
        print("音乐库构建完成！")

    current_song_index = 0

    def play_music(song_index):
        try:
            pygame.mixer.music.load(music_library[song_index])
            pygame.mixer.music.play()
            print(f"正在播放: {music_library[song_index]}")
        except pygame.error as e:
            print(f"无法加载音乐文件 {music_library[song_index]}: {e}")

    def next_song():
        nonlocal current_song_index
        current_song_index = (current_song_index + 1) % len(music_library)
        play_music(current_song_index)

    def previous_song():
        nonlocal current_song_index
        current_song_index = (current_song_index - 1) % len(music_library)
        play_music(current_song_index)

    while True:
        try:
            command = takecommand()
            if command:
                if "播放" in command:
                    play_music(current_song_index)
                elif "下一首" in command:
                    next_song()
                elif "上一首" in command:
                    previous_song()
                elif "退出" in command:
                    pygame.mixer.music.stop()
                    print("音乐播放器已退出。")
                    break
                else:
                    print("未知命令，请重新输入。")
        except Exception as e:
            print(f"发生错误: {e}")

# 使用示例
music_player()
