from setuptools import setup, Extension

# 定义 C 扩展模块
module = Extension('Memory_management', sources=['mymemory.c', 'Memory_management.c'])

# 配置和安装软件包
setup(
    name='mymemory',  # 包名称
    version='1.0',  # 版本号
    description='内存管理的C扩展',  # 描述
    ext_modules=[module],  # 扩展模块列表
)
