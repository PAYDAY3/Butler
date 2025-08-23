# local_interpreter/executor/code_executor.py
# This file implements a sandboxed Python code executor.
# It is designed to run untrusted code from a language model safely.

import io
import sys
import math
from contextlib import redirect_stdout

from ..tools.safe_tools import safe_tool_list
from ..tools.shell_tool import run_shell

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

    # Step 1: Define a whitelist of safe built-in functions.
    # We explicitly exclude dangerous functions like open, eval, __import__, etc.
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

    # Step 2: Define a whitelist of safe modules that can be used by the code.
    safe_modules = {
        'math': math,
    }

    # Step 3: Construct the sandboxed global environment.
    # The key to the sandbox is replacing the default __builtins__ with our
    # own curated dictionary of safe functions.
    sandboxed_globals = {
        "__builtins__": safe_builtins,
        "run_shell": run_shell,  # Add the shell tool here
        **safe_modules,
        **safe_tool_list,
    }

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
