# 该文件是由SWIG自动生成的(http://www.swig.org)。
# 版本3.0.12
# 不要修改这个文件，除非你知道你在做什么——修改
# 使用SWIG接口文件。

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
        import imp

        fp = None
        try:
            fp, pathname, description = imp.find_module(
                "_snowboydetect", [dirname(__file__)]
            )
        except ImportError:
            import _snowboydetect

            return _snowboydetect
        try:
            _mod = imp.load_module("_snowboydetect", fp, pathname, description)
        finally:
            fp and fp.close()
        return _mod

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


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if name == "thisown":
        return self.this.own(value)
    if name == "this":
        if type(value).__name__ == "SwigPyObject":
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if not static:
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if name == "thisown":
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError(
        "'%s' object has no attribute '%s'" % (class_type.__name__, name)
    )


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (
        self.__class__.__module__,
        self.__class__.__name__,
        strthis,
    )


try:
    _object = object
    _newclass = 1
except __builtin__.Exception:

    class _object:
        pass

    _newclass = 0


class SnowboyDetect(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(
        self, SnowboyDetect, name, value
    )
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SnowboyDetect, name)
    __repr__ = _swig_repr

    def __init__(self, resource_filename, model_str):
        this = _snowboydetect.new_SnowboyDetect(resource_filename, model_str)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def Reset(self):
        return _snowboydetect.SnowboyDetect_Reset(self)

    def RunDetection(self, *args):
        return _snowboydetect.SnowboyDetect_RunDetection(self, *args)

    def SetSensitivity(self, sensitivity_str):
        return _snowboydetect.SnowboyDetect_SetSensitivity(self, sensitivity_str)

    def SetHighSensitivity(self, high_sensitivity_str):
        return _snowboydetect.SnowboyDetect_SetHighSensitivity(
            self, high_sensitivity_str
        )

    def GetSensitivity(self):
        return _snowboydetect.SnowboyDetect_GetSensitivity(self)

    def SetAudioGain(self, audio_gain):
        return _snowboydetect.SnowboyDetect_SetAudioGain(self, audio_gain)

    def UpdateModel(self):
        return _snowboydetect.SnowboyDetect_UpdateModel(self)

    def NumHotwords(self):
        return _snowboydetect.SnowboyDetect_NumHotwords(self)

    def ApplyFrontend(self, apply_frontend):
        return _snowboydetect.SnowboyDetect_ApplyFrontend(self, apply_frontend)

    def SampleRate(self):
        return _snowboydetect.SnowboyDetect_SampleRate(self)

    def NumChannels(self):
        return _snowboydetect.SnowboyDetect_NumChannels(self)

    def BitsPerSample(self):
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

    def __init__(self, resource_filename):
        this = _snowboydetect.new_SnowboyVad(resource_filename)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def Reset(self):
        # 重置 VAD
        return _snowboydetect.SnowboyVad_Reset(self)

    def RunVad(self, *args):
        # 运行 VAD 检测
        return _snowboydetect.SnowboyVad_RunVad(self, *args)

    def SetAudioGain(self, audio_gain):
        # 设置音频增益
        return _snowboydetect.SnowboyVad_SetAudioGain(self, audio_gain)

    def ApplyFrontend(self, apply_frontend):    
        return _snowboydetect.SnowboyVad_ApplyFrontend(self, apply_frontend)

    def SampleRate(self):
        # 获取 VAD 的采样率
        return _snowboydetect.SnowboyVad_SampleRate(self)

    def NumChannels(self):
        # 获取 VAD 的通道数
        return _snowboydetect.SnowboyVad_NumChannels(self)

    def BitsPerSample(self):
        # 获取 VAD 每个样本的位数
        return _snowboydetect.SnowboyVad_BitsPerSample(self)

    __swig_destroy__ = _snowboydetect.delete_SnowboyVad
    __del__ = lambda self: None


SnowboyVad_swigregister = _snowboydetect.SnowboyVad_swigregister
SnowboyVad_swigregister(SnowboyVad)

# This file is compatible with both classic and new-style classes.
# 这个文件兼容经典类和新式类。