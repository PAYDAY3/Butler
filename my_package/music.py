from my_package.takecommand import takecommand
import pygame
import os

# 初始化pygame
pygame.mixer.init()

# 音乐播放器函数
def music_player():
    # 播放列表
    playlist = [
        "song1.mp3",
        "song2.mp3",
        "song3.mp3",
        # 添加更多音乐文件路径
    ]

    # 当前播放的音乐文件索引
    current_song_index = 0

    # 加载并播放音乐
    def play_music(song_index):
        try:
            pygame.mixer.music.load(playlist[song_index])
            pygame.mixer.music.play()
            print(f"正在播放: {playlist[song_index]}")
        except pygame.error as e:
            print(f"无法加载音乐文件 {playlist[song_index]}: {e}")
            sys.exit()

    # 播放下一首
    def next_song():
        global current_song_index
        current_song_index = (current_song_index + 1) % len(playlist)
        play_music(current_song_index)

    # 播放上一首
    def previous_song():
        global current_song_index
        current_song_index = (current_song_index - 1) % len(playlist)
        play_music(current_song_index)

    # 主播放循环
    while True:
        # 识别语音命令
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

# 使用示例
music_player()
