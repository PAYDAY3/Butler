from sys import version_info as _swig_python_version_info

# 根据 Python 版本选择导入方式
if _swig_python_version_info >= (2, 7, 0):

    def swig_import_helper():
        import importlib

        pkg = __name__.rpartition(".")[0]
        mname = ".".join((pkg, "_snowboydetect")).lstrip(".")
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module("_snowboydetect")

    _snowboydetect = swig_import_helper()
    del swig_import_helper
    
elif _swig_python_version_info >= (2, 6, 0):

    def swig_import_helper():
        from os.path import dirname
        import importlib.util

        try:
            spec = importlib.util.find_spec("_snowboydetect")
            _mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_mod)
            return _mod
        except ImportError:
            import _snowboydetect
            return _snowboydetect

    _snowboydetect = swig_import_helper()
    del swig_import_helper
else:
    import _snowboydetect
del _swig_python_version_info

try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name: str, value, static: int = 1):
    if name == "thisown":
        return self.this.own(value)
    if name == "this":
        if type(value).__name__ == "SwigPyObject":
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name)
    if method:
        return method(self, value)
    if not static:
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError(f"不能添加属性到 {self}")

def _swig_setattr(self, class_type, name: str, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)

def _swig_getattr(self, class_type, name: str):
    if name == "thisown":
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name)
    if method:
        return method(self)
    raise AttributeError(f"'{class_type.__name__}' 对象没有属性 '{name}'")

def _swig_repr(self):
    try:
        strthis = f"proxy of {self.this.__repr__()}"
    except __builtin__.Exception:
        strthis = ""
    return f"<{self.__class__.__module__}.{self.__class__.__name__}; {strthis} >"

try:
    _object = object
    _newclass = 1
except __builtin__.Exception:

    class _object:
        pass

    _newclass = 0

class SnowboyDetect(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SnowboyDetect, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SnowboyDetect, name)
    __repr__ = _swig_repr

    def __init__(self, resource_filename: str, model_str: str):
        """用资源文件和模型字符串初始化 SnowboyDetect。"""
        this = _snowboydetect.new_SnowboyDetect(resource_filename, model_str)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def Reset(self):
        """重置检测器。"""
        return _snowboydetect.SnowboyDetect_Reset(self)

    def RunDetection(self, *args):
        """用给定的参数运行检测。"""
        return _snowboydetect.SnowboyDetect_RunDetection(self, *args)

    def SetSensitivity(self, sensitivity_str: str):
        """设置灵敏度。"""
        return _snowboydetect.SnowboyDetect_SetSensitivity(self, sensitivity_str)

    def SetHighSensitivity(self, high_sensitivity_str: str):
        """设置高灵敏度。"""
        return _snowboydetect.SnowboyDetect_SetHighSensitivity(self, high_sensitivity_str)

    def GetSensitivity(self) -> str:
        """获取灵敏度。"""
        return _snowboydetect.SnowboyDetect_GetSensitivity(self)

    def SetAudioGain(self, audio_gain: float):
        """设置音频增益。"""
        return _snowboydetect.SnowboyDetect_SetAudioGain(self, audio_gain)

    def UpdateModel(self):
        """更新模型。"""
        return _snowboydetect.SnowboyDetect_UpdateModel(self)

    def NumHotwords(self) -> int:
        """返回热词数量。"""
        return _snowboydetect.SnowboyDetect_NumHotwords(self)

    def ApplyFrontend(self, apply_frontend: bool):
        """应用前端。"""
        return _snowboydetect.SnowboyDetect_ApplyFrontend(self, apply_frontend)

    def SampleRate(self) -> int:
        """返回采样率。"""
        return _snowboydetect.SnowboyDetect_SampleRate(self)

    def NumChannels(self) -> int:
        """返回通道数。"""
        return _snowboydetect.SnowboyDetect_NumChannels(self)

    def BitsPerSample(self) -> int:
        """返回每个样本的位数。"""
        return _snowboydetect.SnowboyDetect_BitsPerSample(self)

    __swig_destroy__ = _snowboydetect.delete_SnowboyDetect
    __del__ = lambda self: None


SnowboyDetect_swigregister = _snowboydetect.SnowboyDetect_swigregister
SnowboyDetect_swigregister(SnowboyDetect)


class SnowboyVad(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SnowboyVad, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SnowboyVad, name)
    __repr__ = _swig_repr

    def __init__(self, resource_filename: str):
        """用资源文件初始化 SnowboyVad。"""
        this = _snowboydetect.new_SnowboyVad(resource_filename)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def Reset(self):
        """重置 VAD。"""
        return _snowboydetect.SnowboyVad_Reset(self)

    def RunVad(self, *args):
        """用给定的参数运行 VAD 检测。"""
        return _snowboydetect.SnowboyVad_RunVad(self, *args)

    def SetAudioGain(self, audio_gain: float):
        """设置音频增益。"""
        return _snowboydetect.SnowboyVad_SetAudioGain(self, audio_gain)

    def ApplyFrontend(self, apply_frontend: bool):
        """应用前端。"""
        return _snowboydetect.SnowboyVad_ApplyFrontend(self, apply_frontend)

    def SampleRate(self) -> int:
        """返回采样率。"""
        return _snowboydetect.SnowboyVad_SampleRate(self)

    def NumChannels(self) -> int:
        """返回通道数。"""
        return _snowboydetect.SnowboyVad_NumChannels(self)

    def BitsPerSample(self) -> int:
        """返回每个样本的位数。"""
        return _snowboydetect.SnowboyVad_BitsPerSample(self)

    __swig_destroy__ = _snowboydetect.delete_SnowboyVad
    __del__ = lambda self: None


SnowboyVad_swigregister = _snowboydetect.SnowboyVad_swigregister
SnowboyVad_swigregister(SnowboyVad)

# 这个文件兼容经典类和新式类。
