#!/usr/bin/env python
import logging
import pyaudio
import collections
import sounddevice as sd
from . import snowboydetect
import time
import wave
import os
from package import Logging
from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
from contextlib import contextmanager
from typing import Callable, List, Optional

logger = Logging.getLogger("snowboy")
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")

def py_error_handler(filename: bytes, line: int, function: bytes, err: int, fmt: bytes) -> None:
    error_message = (f"文件中出现ALSA错误 {filename.decode()}, 行 {line}, "
                     f"函数 {function.decode()}: 错误代码 {err}, "
                     f"消息: {fmt.decode().strip()}")
    logger.error(error_message)

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
    except Exception as e:
        logger.error(f"ALSA 错误处理上下文中发生异常: {e}")
    finally:
        asound.snd_lib_error_set_handler(None)

class RingBuffer(object):
    """保存音频的环形缓冲区"""

    def __init__(self, size: int = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data: bytes) -> None:
        """将数据添加到缓冲区的末尾"""
        self._buf.extend(data)

    def get(self) -> bytes:
        """从缓冲区的开头检索数据并清除它"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


def play_audio_file(fname: str = DETECT_DING) -> None:
    with wave.open(fname, 'rb') as ding_wav:
        ding_data = ding_wav.readframes(ding_wav.getnframes())
        with no_alsa_error():
            audio = sd.OutputStream(samplerate=ding_wav.getframerate(), 
                                    channels=ding_wav.getnchannels())
            audio.start()
            audio.write(ding_data)
            time.sleep(0.2)
            audio.stop()

class HotwordDetector(object):
    def __init__(self, decoder_model: List[str],
                 resource: str = RESOURCE_FILE,
                 sensitivity: List[float] = [],
                 audio_gain: float = 1.0,
                 apply_frontend: bool = False):
        from package import snowboydetect
        
        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), 
            model_str=",".join(decoder_model).encode())
        self.detector.SetAudioGain(audio_gain)
        self.detector.ApplyFrontend(apply_frontend)

        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity * self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())
            
        self.ring_buffer = RingBuffer(self.detector.NumChannels() * self.detector.SampleRate() * 5)
        self._running = False

    def start(self, detected_callback: List[Callable] = [play_audio_file],
              interrupt_check: Callable[[], bool] = lambda: False,
              sleep_time: float = 0.03,
              audio_recorder_callback: Optional[Callable[[str], None]] = None,
              silent_count_threshold: int = 15,
              recording_timeout: int = 100) -> None:
        self._running = True

        def audio_callback(indata: bytes, outdata: bytes, frames: int, time: float, status: sd.CallbackFlags) -> None:
            self.ring_buffer.extend(indata)
            outdata[:] = b'\x00' * len(outdata)

        with no_alsa_error():
            self.audio = sd.InputStream(samplerate=self.detector.SampleRate(), 
                                       channels=self.detector.NumChannels(),
                                       callback=audio_callback)
            self.audio.start()
            
        detected_callback = detected_callback * self.num_hotwords if len(detected_callback) == 1 else detected_callback
        
        assert self.num_hotwords == len(detected_callback), \
            f"错误:您的模型({self.num_hotwords})中的热词不匹配，与回调数量({len(detected_callback)})不匹配"
            
        logger.debug("检测...")

        state = "PASSIVE"
        while self._running:
            if interrupt_check():
                logger.debug("检测语音中断")
                break

            data = self.ring_buffer.get()
            if not data:
                time.sleep(sleep_time)
                continue

            status = self.detector.RunDetection(data)
            if status == -1:
                logger.warning("初始化流或读取音频数据时出错")
                continue
                
            #小型状态机处理关键字后的短语记录
            if state == "PASSIVE":
                if status > 0: #关键词发现
                    self.recordedData = [data]
                    silentCount = 0
                    recordingCount = 0
                    logger.info(f"关键字 {status} 及时检测到: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
                    detected_callback[status - 1]()
                    if callback is not None:
                        callback()

                    if audio_recorder_callback:
                        state = "ACTIVE"
                continue

            elif state == "ACTIVE":
                stopRecording = recordingCount > recording_timeout or (status == -2 and silentCount > silent_count_threshold)
                if stopRecording:
                    filename = self.save_message()
                    audio_recorder_callback(filename)
                    state = "PASSIVE"
                    continue

                recordingCount += 1
                self.recordedData.append(data)
                silentCount = 0 if status == 0 else silentCount + 1

        logger.debug("完成了.")

    def save_message(self) -> str:
        filename = f'output{int(time.time())}.wav'
        data = b''.join(self.recordedData)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 假设音频数据为 16 位
            wf.setsampwidth(self.audio.get_sample_size(
            self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8)))
            wf.setframerate(self.detector.SampleRate())
            wf.writeframes(data)
        logger.debug(f"完成保存: {filename}")
        return filename

    def terminate(self) -> None:
        # self.stream_in.stop_stream()
        # self.stream_in.close()
        if hasattr(self, 'audio'):
            self.audio.stop()
            self.audio.stop()
        self._running = False
