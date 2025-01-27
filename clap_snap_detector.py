import pyaudio
import numpy as np
from scipy.signal import find_peaks
import threading
import time
import wave
import os

class ClapSnapDetector:
    def __init__(self, threshold=0.3, min_frequency=2000, max_frequency=4000):
        self.threshold = threshold
        self.min_frequency = min_frequency
        self.max_frequency = max_frequency
        self.is_listening = False
        self.detected_count = 0
        self.clap_audio = "clap.wav"
        self.snap_audio = "snap.wav"

    def detect_clap_snap(self, audio_data, sample_rate):
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        fft_data = np.fft.fft(audio_array)
        freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)
        
        pos_mask = freqs > 0
        freqs = freqs[pos_mask]
        magnitude = np.abs(fft_data[pos_mask])
        
        peaks, _ = find_peaks(magnitude, height=self.threshold*np.max(magnitude))
        peak_freqs = freqs[peaks]
        
        in_range_peaks = peak_freqs[(peak_freqs >= self.min_frequency) & (peak_freqs <= self.max_frequency)]
        
        if len(in_range_peaks) > 0:
            return True
        return False

    def play_audio(self, file_path):
        if os.path.exists(file_path):
            wf = wave.open(file_path, 'rb')
            p = pyaudio.PyAudio()
            
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
        else:
            print(f"音频文件 {file_path} 不存在")

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
            if self.detect_clap_snap(data, RATE):
                self.detected_count += 1
                print(f"检测到拍手声或啪啪声！ (总计: {self.detected_count})")
                
                if self.detected_count % 2 == 0:
                    print("播放拍手声音效")
                    self.play_audio(self.clap_audio)
                else:
                    print("播放打响指声音效")
                    self.play_audio(self.snap_audio)

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
        time.sleep(60)
    except KeyboardInterrupt:
        print("停止监听...")
    finally:
        detector.stop_listening()
        print(f"总共检测到 {detector.detected_count} 次拍手声或啪啪声")

