# local_interpreter/executor/code_executor.py
# 该文件实现了一个沙盒Python代码执行器。
# 它旨在安全地运行来自语言模型的不受信任代码。
import io
import sys
import math
import os
import importlib
from contextlib import redirect_stdout

from ..tools.safe_tools import safe_tool_list
from ..tools.tool_decorator import TOOL_REGISTRY

import ast
import sys
import types
import inspect
import builtins
import functools
import opcode
import dis
import threading
import time
import gc
import collections
from collections.abc import Mapping
from types import CodeType, FunctionType

class SandboxError(Exception):
    """沙盒执行错误基类"""
    pass

class SecurityError(SandboxError):
    """安全违规错误"""
    pass

class TimeoutError(SandboxError):
    """执行超时错误"""
    pass

class ResourceLimitError(SandboxError):
    """资源限制错误"""
    pass

class RestrictedBuiltins(Mapping):
    """受限制的内置函数集合"""
    def __init__(self, forbidden_attributes, importer_func):
        self.forbidden_attributes = forbidden_attributes

        def safe_getattr(obj, name, *args):
            if name in self.forbidden_attributes:
                raise SecurityError(f"禁止通过 getattr 访问属性: {name}")
            return getattr(obj, name, *args)

        def safe_setattr(obj, name, value):
            if name in self.forbidden_attributes:
                raise SecurityError(f"禁止通过 setattr 设置属性: {name}")
            setattr(obj, name, value)

        def safe_delattr(obj, name):
            if name in self.forbidden_attributes:
                raise SecurityError(f"禁止通过 delattr 删除属性: {name}")
            delattr(obj, name)

        # 允许的安全内置函数白名单
        self._safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'ascii': ascii, 'bin': bin,
            'bool': bool, 'bytearray': bytearray, 'bytes': bytes, 'chr': chr,
            'complex': complex, 'dict': dict, 'dir': dir, 'divmod': divmod,
            'enumerate': enumerate, 'filter': filter, 'float': float, 'format': format,
            'frozenset': frozenset, 'hash': hash, 'hex': hex, 'int': int,
            'isinstance': isinstance, 'issubclass': issubclass, 'iter': iter,
            'len': len, 'list': list, 'map': map, 'max': max, 'min': min,
            'next': next, 'oct': oct, 'ord': ord, 'pow': pow, 'print': print,
            'range': range, 'repr': repr, 'reversed': reversed, 'round': round,
            'set': set, 'slice': slice, 'sorted': sorted, 'str': str, 'sum': sum,
            'tuple': tuple, 'type': type, 'zip': zip,
            'hasattr': hasattr,
            'getattr': safe_getattr,
            'setattr': safe_setattr,
            'delattr': safe_delattr,
            'property': property, 'staticmethod': staticmethod, 'classmethod': classmethod,
            'super': super, 'id': id, 'vars': vars, 'locals': locals, 'globals': globals,
            '__build_class__': __build_class__, '__name__': '__main__', '__debug__': __debug__,
            '__import__': importer_func,
        }
    
    def __getitem__(self, key):
        if key in self._safe_builtins:
            return self._safe_builtins[key]
        raise SecurityError(f"访问受限内置函数 '{key}'")
    
    def __iter__(self):
        return iter(self._safe_builtins)
    
    def __len__(self):
        return len(self._safe_builtins)

class SafeImporter:
    """安全的模块导入器"""
    def __init__(self, allowed_modules=None):
        # 允许导入的模块白名单
        self.allowed_modules = allowed_modules or {
            'math', 'cmath', 'decimal', 'fractions', 'random', 'statistics',
            'datetime', 'calendar', 'collections', 'heapq', 'bisect', 'array',
            'queue', 'itertools', 'functools', 'operator', 'copy', 'pprint',
            'string', 're', 'json', 'struct', 'hashlib', 'hmac', 'secrets',
            'time', 'threading', 'contextlib', 'abc', 'atexit', 'logging',
            'typing', 'enum', 'numbers', 'html', 'xml', 'unicodedata', 'base64',
            'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'csv', 'configparser',
            'argparse', 'getopt', 'readline', 'getpass', 'cmd', 'shlex', 'sysconfig',
        }
        
        # 模块特定的允许属性
        self.module_attributes = {
            'sys': {'version', 'version_info', 'platform', 'argv', 'path', 'modules'},
            'os': {'name', 'environ', 'pathsep', 'sep', 'linesep'},
        }
    
    def import_module(self, name, globals=None, locals=None, fromlist=(), level=0):
        """安全的模块导入函数"""
        # 检查模块是否允许导入
        if name not in self.allowed_modules:
            raise SecurityError(f"禁止导入模块: {name}")
        
        # 实际导入模块
        module = __import__(name, globals, locals, fromlist, level)
        
        # 如果是从模块导入特定属性，检查这些属性是否允许
        if fromlist:
            for attr in fromlist:
                if attr.startswith('_'):
                    raise SecurityError(f"禁止访问以下划线开头的属性: {attr}")
                
                # 检查模块特定的属性限制
                if name in self.module_attributes and attr not in self.module_attributes[name]:
                    raise SecurityError(f"禁止从模块 {name} 导入属性: {attr}")
        
        return module

class ASTValidator(ast.NodeVisitor):
    """AST 验证器，用于检查和限制代码结构"""
    
    def __init__(self):
        # 允许的节点类型白名单
        self.allowed_nodes = {
            # 模块和函数定义
            ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda,
            
            # 控制流
            ast.If, ast.For, ast.AsyncFor, ast.While, ast.Break, ast.Continue,
            ast.Try, ast.With, ast.AsyncWith, ast.Raise, ast.Assert, ast.Pass,
            
            # 作用域和变量
            ast.Global, ast.Nonlocal, ast.Delete, ast.Assign, ast.AugAssign, ast.AnnAssign,
            ast.NamedExpr,
            
            # 表达式
            ast.Expr, ast.UnaryOp, ast.BinOp, ast.BoolOp, ast.Compare, ast.Call,
            ast.IfExp, ast.Attribute, ast.Subscript, ast.Starred, ast.Name, ast.Constant,
            ast.JoinedStr, ast.FormattedValue,
            
            # 集合
            ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.SetComp,
            ast.DictComp, ast.GeneratorExp,
            
            # 其他
            ast.Slice, ast.Index, ast.ExtSlice, ast.comprehension, ast.arguments,
            ast.arg, ast.keyword, ast.alias, ast.withitem, ast.excepthandler,
        }
        
        # 禁止的节点类型黑名单
        self.forbidden_nodes = {
            ast.Yield, ast.YieldFrom, ast.Await,  # 生成器和协程
        }
        
        # 禁止的函数和属性黑名单
        self.forbidden_calls = {
            'eval', 'exec', 'execfile', 'compile', 'input', 'open',
            'exit', 'quit', 'help', 'license', 'copyright', 'credits',
        }
        
        self.forbidden_attributes = {
            '__subclasses__', '__bases__', '__mro__', '__class__', '__dict__',
            '__globals__', '__closure__', '__code__', '__func__', '__self__',
            '__module__', '__builtins__', '__import__', '__getattribute__',
            '__getattr__', '__setattr__', '__delattr__', '__dir__', '__get__',
            '__set__', '__delete__', '__slots__', '__weakref__', '__next__',
            '__enter__', '__exit__', '__aenter__', '__aexit__', '__iter__',
            '__anext__', '__await__', '__call__', '__new__', '__init__',
            '__init_subclass__', '__prepare__', '__instancecheck__',
            '__subclasscheck__', '__getitem__', '__setitem__', '__delitem__',
            '__contains__', '__len__', '__iter__', '__reversed__', '__add__',
            '__sub__', '__mul__', '__matmul__', '__truediv__', '__floordiv__',
            '__mod__', '__divmod__', '__pow__', '__lshift__', '__rshift__',
            '__and__', '__xor__', '__or__', '__radd__', '__rsub__', '__rmul__',
            '__rmatmul__', '__rtruediv__', '__rfloordiv__', '__rmod__',
            '__rdivmod__', '__rpow__', '__rlshift__', '__rrshift__', '__rand__',
            '__rxor__', '__ror__', '__iadd__', '__isub__', '__imul__',
            '__imatmul__', '__itruediv__', '__ifloordiv__', '__imod__',
            '__ipow__', '__ilshift__', '__irshift__', '__iand__', '__ixor__',
            '__ior__', '__neg__', '__pos__', '__abs__', '__invert__', '__complex__',
            '__int__', '__float__', '__index__', '__round__', '__trunc__',
            '__floor__', '__ceil__', '__bool__', '__hash__', '__str__',
            '__repr__', '__bytes__', '__format__', '__lt__', '__le__', '__eq__',
            '__ne__', '__gt__', '__ge__', '__getnewargs__', '__getnewargs_ex__',
            '__getstate__', '__setstate__', '__reduce__', '__reduce_ex__',
            '__sizeof__', '__dir__', '__init__', '__subclasshook__',
        }
    
    def validate(self, node):
        """验证 AST 节点"""
        if type(node) not in self.allowed_nodes:
            raise SecurityError(f"禁止的语法结构: {type(node).__name__}")
        
        if type(node) in self.forbidden_nodes:
            raise SecurityError(f"明确禁止的语法结构: {type(node).__name__}")
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """检查导入语句"""
        for alias in node.names:
            if alias.name.startswith('_'):
                raise SecurityError(f"禁止导入以下划线开头的模块: {alias.name}")
            
            # 检查模块黑名单
            forbidden_modules = {'io', 'socket', 'subprocess', 'ctypes',
                                'mmap', 'fcntl', 'select', 'selectors', 'signal',
                                'resource', 'pwd', 'grp', 'termios', 'tty', 'pty',
                                'fcntl', 'posix', 'nt', '_winreg', 'winreg', 'msvcrt'}
            
            if alias.name in forbidden_modules:
                raise SecurityError(f"禁止导入模块: {alias.name}")
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """检查从模块导入语句"""
        if node.module and node.module.startswith('_'):
            raise SecurityError(f"禁止从以下划线开头的模块导入: {node.module}")
        
        # 检查模块黑名单
        forbidden_modules = {'io', 'socket', 'subprocess', 'ctypes',
                            'mmap', 'fcntl', 'select', 'selectors', 'signal',
                            'resource', 'pwd', 'grp', 'termios', 'tty', 'pty',
                            'fcntl', 'posix', 'nt', '_winreg', 'winreg', 'msvcrt'}
        
        if node.module in forbidden_modules:
            raise SecurityError(f"禁止从模块导入: {node.module}")
        
        # 检查导入的属性
        for alias in node.names:
            if alias.name.startswith('_'):
                raise SecurityError(f"禁止导入以下划线开头的属性: {alias.name}")
            
            if alias.name in self.forbidden_attributes:
                raise SecurityError(f"禁止导入属性: {alias.name}")
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """检查函数调用"""
        # 检查直接调用危险函数
        if isinstance(node.func, ast.Name):
            if node.func.id in self.forbidden_calls:
                raise SecurityError(f"禁止调用函数: {node.func.id}")
        
        # 检查调用危险方法
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in self.forbidden_calls:
                raise SecurityError(f"禁止调用方法: {node.func.attr}")
            
            if node.func.attr in self.forbidden_attributes:
                raise SecurityError(f"禁止调用方法: {node.func.attr}")
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """检查属性访问"""
        if node.attr in self.forbidden_attributes:
            raise SecurityError(f"禁止访问属性: {node.attr}")
        
        self.generic_visit(node)

class BytecodeValidator:
    """字节码验证器，用于检查和过滤危险操作码"""
    
    def __init__(self):
        # Build the list of allowed opcodes dynamically to support multiple Python versions.
        allowed_op_names = [
            'POP_TOP', 'ROT_TWO', 'ROT_THREE', 'ROT_FOUR', 'DUP_TOP', 'DUP_TOP_TWO', 'NOP',
            'UNARY_POSITIVE', 'UNARY_NEGATIVE', 'UNARY_NOT', 'UNARY_INVERT',
            'BINARY_POWER', 'BINARY_MULTIPLY', 'BINARY_FLOOR_DIVIDE', 'BINARY_TRUE_DIVIDE',
            'BINARY_MODULO', 'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_SUBSCR',
            'BINARY_LSHIFT', 'BINARY_RSHIFT', 'BINARY_AND', 'BINARY_XOR', 'BINARY_OR',
            'INPLACE_ADD', 'INPLACE_SUBTRACT', 'INPLACE_MULTIPLY', 'INPLACE_FLOOR_DIVIDE',
            'INPLACE_TRUE_DIVIDE', 'INPLACE_MODULO', 'INPLACE_POWER', 'INPLACE_LSHIFT',
            'INPLACE_RSHIFT', 'INPLACE_AND', 'INPLACE_XOR', 'INPLACE_OR',
            'STORE_SUBSCR', 'DELETE_SUBSCR', 'GET_ITER', 'GET_YIELD_FROM_ITER',
            'PRINT_EXPR', 'LOAD_BUILD_CLASS', 'YIELD_FROM', 'SET_ADD', 'LIST_APPEND',
            'MAP_ADD', 'LOAD_CONST', 'LOAD_NAME', 'STORE_NAME', 'LOAD_GLOBAL', 'LOAD_ATTR',
            'COMPARE_OP', 'IMPORT_NAME', 'IMPORT_FROM', 'JUMP_FORWARD', 'JUMP_BACKWARD',
            'JUMP_IF_FALSE_OR_POP', 'JUMP_IF_TRUE_OR_POP', 'JUMP_ABSOLUTE',
            'POP_JUMP_IF_FALSE', 'POP_JUMP_IF_TRUE', 'LOAD_FAST', 'STORE_FAST',
            'DELETE_FAST', 'LOAD_CLOSURE', 'LOAD_DEREF', 'STORE_DEREF', 'DELETE_DEREF',
            'RAISE_VARARGS', 'CALL', 'CALL_FUNCTION', 'CALL_FUNCTION_KW', 'CALL_FUNCTION_EX',
            'LOAD_METHOD', 'CALL_METHOD', 'LIST_EXTEND', 'SET_UPDATE', 'DICT_UPDATE',
            'DICT_MERGE', 'FORMAT_VALUE', 'BUILD_CONST_KEY_MAP', 'BUILD_STRING',
            'BUILD_TUPLE', 'BUILD_LIST', 'BUILD_SET', 'BUILD_MAP', 'SETUP_ANNOTATIONS',
            'LOAD_ASSERTION_ERROR', 'LIST_TO_TUPLE', 'RETURN_CONST', 'BINARY_OP',
            # Python 3.9+
            'IS_OP', 'CONTAINS_OP', 'JUMP_IF_NOT_EXC_MATCH', 'RERAISE', 'GEN_START',
            # Python 3.10+
            'ROT_FOUR',
            # Python 3.11+
            'PUSH_NULL', 'PRECALL', 'RESUME', 'RETURN_GENERATOR', 'SEND',
            'SWAP', 'COPY', 'CACHE', 'PUSH_EXC_INFO', 'CHECK_EXC_MATCH',
            # Python 3.12+
            'END_FOR',
            # Other
            'LOAD_FAST_AND_CLEAR'
        ]
        self.allowed_opcodes = {
            op for op_name in allowed_op_names if (op := opcode.opmap.get(op_name)) is not None
        }
        
        # For Python 3.8, use opcode.opmap.get to avoid errors on missing opcodes
        _forbidden_op_names = [
            'IMPORT_STAR',  # 禁止 from module import *
            'EXEC_STMT',    # (Python 2) 禁止 exec 语句
        ]
        self.forbidden_opcodes = {
            op for op_name in _forbidden_op_names if (op := opcode.opmap.get(op_name)) is not None
        }

        # Add opcodes needed for control flow to the allowed list
        # Opcodes for loops, try/except, with statements
        control_flow_opcodes = [
            'FOR_ITER',
            'SETUP_LOOP', 'BREAK_LOOP', 'CONTINUE_LOOP',
            'SETUP_EXCEPT', 'POP_EXCEPT', 'SETUP_FINALLY', 'END_FINALLY',
            'SETUP_WITH', 'WITH_EXCEPT_START', 'POP_BLOCK',
            'GET_AWAITABLE', 'GET_AITER', 'GET_ANEXT', 'END_ASYNC_FOR',
            'BEFORE_ASYNC_WITH', 'SETUP_ASYNC_WITH', 'GET_AEXIT_CORO'
        ]
        for op_name in control_flow_opcodes:
            if (op := opcode.opmap.get(op_name)) is not None:
                self.allowed_opcodes.add(op)
    
    def validate(self, code_obj):
        """验证字节码"""
        instructions = dis.get_instructions(code_obj)
        
        for instr in instructions:
            if instr.opcode in self.forbidden_opcodes:
                raise SecurityError(f"禁止的操作码: {instr.opname}")
            
            if instr.opcode not in self.allowed_opcodes:
                raise SecurityError(f"不允许的操作码: {instr.opname}")

class ResourceMonitor(threading.Thread):
    """资源监视器，用于监控代码执行的资源使用情况"""
    
    def __init__(self, interval=0.1, memory_limit=100*1024*1024, instruction_limit=1000000):
        super().__init__()
        self.interval = interval
        self.memory_limit = memory_limit
        self.instruction_limit = instruction_limit
        self.stop_event = threading.Event()
        self.instruction_count = 0
        self.max_memory = 0
        self.daemon = True
    
    def run(self):
        """监控资源使用"""
        while not self.stop_event.wait(self.interval):
            # 检查内存使用
            current_memory = self.get_memory_usage()
            self.max_memory = max(self.max_memory, current_memory)
            
            if current_memory > self.memory_limit:
                raise ResourceLimitError(f"内存使用超过限制: {current_memory} > {self.memory_limit}")
    
    def stop(self):
        """停止监控"""
        self.stop_event.set()
    
    def get_memory_usage(self):
        """获取当前内存使用量"""
        # 这是一个简化的实现，实际中可能需要更精确的内存监控
        return len(gc.get_objects()) * 100  # 近似值
    
    def count_instruction(self):
        """计数指令执行"""
        self.instruction_count += 1
        if self.instruction_count > self.instruction_limit:
            raise ResourceLimitError(f"指令执行超过限制: {self.instruction_count} > {self.instruction_limit}")

class Sandbox:
    """Python 沙盒执行环境"""
    
    def __init__(self, timeout=30, memory_limit=100*1024*1024, instruction_limit=1000000):
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.instruction_limit = instruction_limit
        self.ast_validator = ASTValidator()
        self.bytecode_validator = BytecodeValidator()
        self.importer = SafeImporter()
        self.resource_monitor = ResourceMonitor(
            memory_limit=memory_limit, 
            instruction_limit=instruction_limit
        )
    
    def create_restricted_globals(self):
        """创建受限制的全局变量环境"""
        restricted_globals = {
            '__builtins__': RestrictedBuiltins(
                self.ast_validator.forbidden_attributes, self.importer.import_module
            ),
            '__name__': '__main__',
            '__file__': None,
            '__package__': None,
            '__doc__': None,
            '__loader__': None,
            '__spec__': None,
            '__import__': self.importer.import_module,
        }
        return restricted_globals
    
    def execute(self, code, globals_dict=None, locals_dict=None):
        """
        在沙盒中执行代码
        
        Args:
            code (str): 要执行的Python代码
            globals_dict (dict): 全局变量字典，如果为None则使用受限环境
            locals_dict (dict): 局部变量字典
        
        Returns:
            执行结果
        
        Raises:
            SecurityError: 如果检测到安全违规
            TimeoutError: 如果执行超时
            ResourceLimitError: 如果资源使用超过限制
        """
        # 解析代码为AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SandboxError(f"语法错误: {e}")
        
        # 验证AST
        try:
            self.ast_validator.validate(tree)
        except SecurityError as e:
            raise e
        
        # 编译AST
        try:
            code_obj = compile(tree, '<string>', 'exec')
        except Exception as e:
            raise SandboxError(f"编译错误: {e}")
        
        # 验证字节码
        try:
            self.bytecode_validator.validate(code_obj)
        except SecurityError as e:
            raise e
        
        # 准备执行环境
        if globals_dict is None:
            globals_dict = self.create_restricted_globals()
        
        if locals_dict is None:
            locals_dict = globals_dict
        
        # 启动资源监控
        self.resource_monitor.start()
        
        # 设置执行超时
        result = None
        exception = None
        
        def run_code():
            nonlocal result, exception

            def trace_dispatch(frame, event, arg):
                try:
                    if event == 'opcode':
                        self.resource_monitor.count_instruction()
                except ResourceLimitError as e:
                    # Must raise an exception here to stop execution.
                    # This is a bit of a hack, as there's no clean way to stop exec.
                    raise e
                return trace_dispatch

            sys.settrace(trace_dispatch)
            try:
                # 执行代码
                exec(code_obj, globals_dict, locals_dict)
                result = (globals_dict, locals_dict)
            except Exception as e:
                exception = e
            finally:
                sys.settrace(None)
        
        # 在单独的线程中执行代码
        thread = threading.Thread(target=run_code)
        thread.daemon = True
        thread.start()
        
        # 等待执行完成或超时
        thread.join(self.timeout)
        
        # 停止资源监控
        self.resource_monitor.stop()
        
        # 检查执行结果
        if thread.is_alive():
            raise TimeoutError(f"执行超时: {self.timeout}秒")
        
        if exception:
            if isinstance(exception, SecurityError):
                raise exception
            elif isinstance(exception, ResourceLimitError):
                raise exception
            else:
                raise SandboxError(f"执行错误: {exception}")
        
        return result

# 示例使用
if __name__ == '__main__':
    def run_test(name, code, sandbox_factory):
        print(f"\n--- {name} ---")
        try:
            sandbox = sandbox_factory()
            output_catcher = io.StringIO()
            with redirect_stdout(output_catcher):
                sandbox.execute(code)
            output = output_catcher.getvalue()
            if output:
                print("代码输出:\n" + output.strip())
            else:
                print("代码成功执行，无输出。")
        except Exception as e:
            print(f"成功捕获错误: {e}")

    # 1. Safe code
    run_test(
        "1. 测试安全的代码 (循环和打印)",
        """
total = 0
for i in range(10):
    total += i
print(f"计算结果: {total}")
        """,
        lambda: Sandbox(timeout=5, instruction_limit=30000)
    )

    # 2. Forbidden import
    run_test(
        "2. 测试禁止的导入 (subprocess)",
        "import subprocess",
        lambda: Sandbox()
    )

    # 3. Instruction limit (now timeout)
    run_test(
        "3. 测试指令数量限制 (无限循环)",
        "while True: pass",
        lambda: Sandbox(timeout=2, instruction_limit=20000) # shorter timeout to ensure it triggers
    )

    # 4. Timeout
    run_test(
        "4. 测试执行超时 (time.sleep)",
        "import time; time.sleep(5)",
        lambda: Sandbox(timeout=2)
    )

    # 5. Forbidden getattr
    run_test(
        "5. 测试禁止的属性访问 (getattr)",
        "getattr(int, '__' + 'subclasses' + '__')()",
        lambda: Sandbox()
    )

    # 6. Safe sys/os import
    def sys_os_test_sandbox():
        s = Sandbox()
        s.importer.allowed_modules.add('sys')
        s.importer.allowed_modules.add('os')
        return s
    run_test(
        "6. 测试安全的 'sys' 和 'os' 模块导入",
        """
import sys
import os
print(f'Python platform: {sys.platform}')
print(f'OS name: {os.name}')
        """,
        sys_os_test_sandbox
    )

    # 7. Memory limit
    run_test(
        "7. 测试内存限制",
        "a = [i for i in range(20000)]",
        lambda: Sandbox(memory_limit=1024*1024)
    )
