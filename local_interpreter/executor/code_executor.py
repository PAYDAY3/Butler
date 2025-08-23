# local_interpreter/executor/code_executor.py
# This file implements a sandboxed Python code executor.
# It is designed to run untrusted code from a language model safely.

import io
import sys
import math
import os
import importlib
from contextlib import redirect_stdout

from ..tools.safe_tools import safe_tool_list
from ..tools.tool_decorator import TOOL_REGISTRY

def load_tools():
    """
    Dynamically imports all modules in the 'tools' directory to ensure
    that all functions decorated with @tool are registered in the TOOL_REGISTRY.
    """
    tools_dir = os.path.dirname(__file__)
    # Go up one level to the 'local_interpreter' directory, then down into 'tools'
    tools_path = os.path.join(os.path.dirname(tools_dir), "tools")

    for filename in os.listdir(tools_path):
        # Import all python files in the tools directory
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"local_interpreter.tools.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
            except Exception as e:
                print(f"Error loading tool module {module_name}: {e}")

def execute_python_code(code: str) -> tuple[str, bool]:
    """
    Executes a string of Python code in a sandboxed environment and captures its output.
    This sandbox is created by providing a custom, restricted global environment
    to the `exec` function, which prevents access to dangerous built-in functions.

    Args:
        code: The Python code to execute.

    Returns:
        A tuple containing:
        - The captured stdout from the executed code as a string.
        - A boolean indicating success (True) or failure (False).
    """
    # print(f"Executor received code to run in sandbox:\n---\n{code}\n---")

    # Step 1: Dynamically load all available tools.
    # This populates the TOOL_REGISTRY.
    load_tools()

    # Step 2: Define a whitelist of safe built-in functions.
    safe_builtins = {
        'print': print,
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'range': range,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'round': round,
        'sorted': sorted,
        'type': type,
    }

    # Step 3: Define a whitelist of safe modules.
    safe_modules = {
        'math': math,
    }

    # Step 4: Construct the sandboxed global environment.
    # Start with built-ins and safe modules.
    sandboxed_globals = {
        "__builtins__": safe_builtins,
        **safe_modules,
        **safe_tool_list,
    }

    # Add all registered tools to the sandbox globals.
    for tool_name, tool_data in TOOL_REGISTRY.items():
        sandboxed_globals[tool_name] = tool_data["function"]


    # Use a string buffer to capture any output from print() statements.
    buffer = io.StringIO()

    try:
        # Step 4: Execute the code.
        # The 'exec' function is used here, but it is constrained by the
        # 'sandboxed_globals'. The code can only access what we have explicitly
        # allowed in the dictionaries above.
        with redirect_stdout(buffer):
            exec(code, sandboxed_globals)

        output = buffer.getvalue()
        # print("Execution successful.")
        return output, True
    except Exception as e:
        # If the code tries to do anything forbidden (e.g., use 'open'),
        # it will raise an exception (e.g., NameError), which we catch here.
        error_message = f"Error during execution: {type(e).__name__}: {e}"
        # print(error_message, file=sys.stderr)
        return error_message, False
    finally:
        buffer.close()
