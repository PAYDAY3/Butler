#!/usr/bin/env python

import collections
import sounddevice as sd
from . import snowboydetect
import time
import wave
import os
from my_package.Logging import Logging
from ctypes import *
from contextlib import contextmanager

logging.basicConfig()
logger = Logging.getLogger("snowboy")
logger.setLevel(logging.INFO)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")

def py_error_handler(filename, line, function, err, fmt):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

class RingBuffer(object):
    """保存音频的环形缓冲区"""

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """将数据添加到缓冲区的末尾"""
        self._buf.extend(data)

    def get(self):
        """从缓冲区的开头检索数据并清除它"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


def play_audio_file(fname=DETECT_DING):
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    with no_alsa_error():
        audio = sd.Stream(samplerate=ding_wav.getframerate(), channels=ding_wav.getnchannels(), callback=lambda outdata, frames, time, status: outdata[:len(ding_data)])
        audio.start()
        audio.write(ding_data)
        time.sleep(0.2)
        audio.stop()

class HotwordDetector(object):

    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity=[],
                 audio_gain=1,
                 apply_frontend=False):

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
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

        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5)

    def start(self, detected_callback=play_audio_file,
              interrupt_check=lambda: False,
              sleep_time=0.03,
              audio_recorder_callback=None,
              silent_count_threshold=15,
              recording_timeout=100):
        self._running = True

        def audio_callback(indata, outdata, frames, time, status):
            self.ring_buffer.extend(indata)
            play_data = chr(0) * len(indata)
            return play_data, pyaudio.paContinue

        with no_alsa_error():
            self.audio = sd.Stream(samplerate=self.detector.SampleRate(), channels=self.detector.NumChannels(), callback=audio_callback)
            self.audio.start()
            
        if interrupt_check():
            logger.debug("检测语音返回")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "错误:您的模型(%d)中的热词不匹配 " \
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))

        logger.debug("检测...")

        state = "PASSIVE"
        while self._running is True:
            if interrupt_check():
                logger.debug("检测语音中断")
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            status = self.detector.RunDetection(data)
            if status == -1:
                logger.warning("初始化流或读取音频数据时出错")

            #小型状态机处理关键字后的短语记录
            if state == "PASSIVE":
                if status > 0: #关键词发现
                    self.recordedData = []
                    self.recordedData.append(data)
                    silentCount = 0
                    recordingCount = 0
                    message = "关键字 " + str(status) + " 及时检测到: "
                    message += time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(time.time()))
                    logger.info(message)
                    callback = detected_callback[status-1]
                    if callback is not None:
                        callback()

                    if audio_recorder_callback is not None:
                        state = "ACTIVE"
                    continue

            elif state == "ACTIVE":
                stopRecording = False
                if recordingCount > recording_timeout:
                    stopRecording = True
                elif status == -2: #沉默了
                    if silentCount > silent_count_threshold:
                        stopRecording = True
                    else:
                        silentCount = silentCount + 1
                elif status == 0: #声音发现
                    silentCount = 0

                if stopRecording == True:
                    fname = self.saveMessage()
                    audio_recorder_callback(fname)
                    state = "PASSIVE"
                    continue

                recordingCount = recordingCount + 1
                self.recordedData.append(data)

        logger.debug("finished.")

    def saveMessage(self):
        filename = 'output' + str(int(time.time())) + '.wav'
        data = b''.join(self.recordedData)

        # 使用wave保存数据
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2) # 假设音频数据为 16 位
        wf.setsampwidth(self.audio.get_sample_size(
            self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8)))
        wf.setframerate(self.detector.SampleRate())        
        wf.writeframes(data)
        wf.close()
        logger.debug("完成保存: " + filename)
        return filename

    def terminate(self):
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.stop()
        self._running = False
