import pyaudio
import numpy as np
from scipy.signal import find_peaks, butter, lfilter
import threading
import time
import subprocess
import os

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def noise_reduction(audio_data):
    # 转换音频数据到频域
    fft_data = np.fft.fft(audio_data)  # 对音频数据进行快速傅里叶变换（FFT），将其从时域转换到频域
    magnitude = np.abs(fft_data)       # 获取频域数据的幅度
    phase = np.angle(fft_data)         # 获取频域数据的相位
    
    # 估计噪声功率谱
    noise_magnitude = np.mean(magnitude[:int(0.1 * len(magnitude))])  # 估计噪声功率谱，使用频率范围内的一部分数据计算噪声平均值
    
    # 从信号中减去噪声
    magnitude = magnitude - noise_magnitude  # 从信号中减去噪声幅度
    magnitude[magnitude < 0] = 0             # 确保幅度不为负值
    
    # 重构信号
    fft_data = magnitude * np.exp(1j * phase)  # 使用新的幅度和原始相位重建频域信号
    denoised_audio = np.fft.ifft(fft_data)     # 对频域信号进行逆快速傅里叶变换（iFFT），将其转换回时域
    return np.real(denoised_audio)             # 返回去噪后的实数部分音频数据
       
class ClapSnapDetector:
    def __init__(self, threshold=0.3, min_frequency_clap=1000, max_frequency_clap=2000, min_frequency_snap=2000, max_frequency_snap=4000):
        self.threshold = threshold
        self.min_frequency_clap = min_frequency_clap
        self.max_frequency_clap = max_frequency_clap
        self.min_frequency_snap = min_frequency_snap
        self.max_frequency_snap = max_frequency_snap
        self.is_listening = False
        self.detected_count_clap = 0
        self.detected_count_snap = 0

    def detect_clap_snap(self, audio_data, sample_rate):
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        denoised_data = noise_reduction(audio_array)
        filtered_data = bandpass_filter(audio_array, self.min_frequency_clap, self.max_frequency_snap, sample_rate)
        fft_data = np.fft.fft(filtered_data)
        freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)
        
        pos_mask = freqs > 0
        freqs = freqs[pos_mask]
        magnitude = np.abs(fft_data[pos_mask])
        
        peaks, _ = find_peaks(magnitude, height=self.threshold*np.max(magnitude))
        peak_freqs = freqs[peaks]
        
        # 检查鼓掌
        clap_peaks = peak_freqs[(peak_freqs >= self.min_frequency_clap) & (peak_freqs <= self.max_frequency_clap)]
        if len(clap_peaks) > 0:
            return "clap"
        
        # 检查响指
        snap_peaks = peak_freqs[(peak_freqs >= self.min_frequency_snap) & (peak_freqs <= self.max_frequency_snap)]
        if len(snap_peaks) > 0:
            return "snap"
        
        return None

    def open_program(self, sound_type):
        """
        根据声音类型启动相应的程序。
        这里你可以根据需要更改为不同的程序路径。
        """
        if sound_type == "clap":
            print("启动程序: 击掌对应程序")
            # 启动击掌对应的程序
            subprocess.run(["jarvis/jarvis.py"])
        elif sound_type == "snap":
            print("启动程序: 响指对应程序")
            # 启动响指对应的程序
            subprocess.run(["jarvis/jarvis.py"])

    def listen(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("开始监听拍手声或啪啪声...")
        self.is_listening = True

        while self.is_listening:
            data = stream.read(CHUNK)
            detected_sound = self.detect_clap_snap(data, RATE)
            if detected_sound == "clap":
                self.detected_count_clap += 1
                print(f"检测到击掌声！ (总计: {self.detected_count_clap})")
                self.open_program("clap")  # 当检测到击掌声时启动程序
            elif detected_sound == "snap":
                self.detected_count_snap += 1
                print(f"检测到响指声！ (总计: {self.detected_count_snap})")
                self.open_program("snap")  # 当检测到响指声时启动程序

        stream.stop_stream()
        stream.close()
        p.terminate()

    def start_listening(self):
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

    def stop_listening(self):
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join()

if __name__ == "__main__":
    detector = ClapSnapDetector()
    try:
        detector.start_listening()
        time.sleep(60)  # 听 60 秒
    except KeyboardInterrupt:
        print("停止监听...")
    finally:
        detector.stop_listening()
        print(f"总共检测到 {detector.detected_count_clap} 次击掌声和 {detector.detected_count_snap} 次响指声")
