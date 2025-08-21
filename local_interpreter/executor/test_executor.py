# This script is for testing the sandboxed code executor.
from .code_executor import execute_python_code
import math

def run_tests():
    """
    Runs a series of tests on the sandboxed executor.
    """
    print("--- Running Sandbox Tests ---")

    # Test Case 1: Code that should be allowed
    print("\n[Test 1] Running allowed code...")
    # The 'math' module is pre-imported into the sandbox, so the code doesn't need to import it.
    code_allowed = "print('The square root of 16 is:', math.sqrt(16))"
    output, success = execute_python_code(code_allowed)
    print(f"Success: {success}")
    print(f"Output: {output.strip()}")
    assert success
    assert "4.0" in output

    # Test Case 2: Code that tries to access the file system (should be blocked)
    print("\n[Test 2] Running disallowed code (file access)...")
    code_disallowed_file = "f = open('malicious.txt', 'w')\nf.write('hacked')\nf.close()"
    output, success = execute_python_code(code_disallowed_file)
    print(f"Success: {success}")
    print(f"Output: {output.strip()}")
    assert not success
    assert "NameError" in output and "open" in output

    # Test Case 3: Code that tries to import a dangerous module (should be blocked)
    print("\n[Test 3] Running disallowed code (import os)...")
    code_disallowed_import = "import os"
    output, success = execute_python_code(code_disallowed_import)
    print(f"Success: {success}")
    print(f"Output: {output.strip()}")
    assert not success
    # The error should be ImportError because the import machinery itself fails.
    assert "ImportError" in output and "__import__ not found" in output

    # Test Case 4: Code that uses an allowed PC tool
    print("\n[Test 4] Running allowed code (PC tool)...")
    code_pc_tool = "stats = get_system_stats()\nprint(type(stats))"
    output, success = execute_python_code(code_pc_tool)
    print(f"Success: {success}")
    print(f"Output: {output.strip()}")
    assert success
    assert "<class 'dict'>" in output

    # Test Case 5: Code that uses an allowed embedded tool
    print("\n[Test 5] Running allowed code (Embedded tool)...")
    code_embedded_tool = "result = set_gpio_pin(17, True)\nprint(result)"
    output, success = execute_python_code(code_embedded_tool)
    print(f"Success: {success}")
    print(f"Output: {output.strip()}")
    assert success
    assert "Pin 17 set to True" in output

    # Test Case 6: Code that tries to misuse a tool (directory traversal)
    print("\n[Test 6] Running disallowed tool action (directory traversal)...")
    code_tool_misuse = "list_safe_directory('../../..')"
    output, success = execute_python_code(code_tool_misuse)
    print(f"Success: {success}")
    print(f"Output: {output.strip()}")
    assert not success
    assert "PermissionError" in output

    print("\n--- All Tests Passed ---")

if __name__ == "__main__":
    run_tests()
