# local_interpreter/tools/safe_tools.py
import os
import time

# Define a safe working directory. Code from the sandbox can only access files here.
# For simplicity, we'll create it inside the project.
SAFE_WORKING_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))

# --- Filesystem Tools ---

def list_safe_directory(sub_path="."):
    """
    Lists the contents of a subdirectory within the SAFE_WORKING_DIR.
    Prevents directory traversal attacks.
    """
    # Ensure the safe directory exists
    if not os.path.exists(SAFE_WORKING_DIR):
        os.makedirs(SAFE_WORKING_DIR)

    # Sanitize the sub_path to prevent traversal
    safe_path = os.path.abspath(os.path.join(SAFE_WORKING_DIR, sub_path))

    if not safe_path.startswith(SAFE_WORKING_DIR):
        raise PermissionError("Access denied: Path is outside the safe working directory.")

    return os.listdir(safe_path)

# --- System & Hardware Tools ---

def get_system_stats():
    """
    Gets basic system stats (CPU and Memory usage).
    This is a simplified, dependency-free implementation for Linux-based systems.
    """
    # Simplified CPU usage (not super accurate, but dependency-free)
    try:
        with open('/proc/stat', 'r') as f:
            line = f.readline()
        cpu_times = [int(v) for v in line.split()[1:]]
        idle_time = cpu_times[3]
        total_time = sum(cpu_times)
        # This is a very rough snapshot, a real implementation would compare over time
        cpu_usage = 100 * (1 - idle_time / total_time)
    except (IOError, IndexError, ValueError):
        cpu_usage = "N/A (Non-Linux or permission error)"

    # Memory usage
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        mem_total = int(lines[0].split()[1])
        mem_free = int(lines[1].split()[1])
        mem_used = mem_total - mem_free
        mem_percent = (mem_used / mem_total) * 100
    except (IOError, IndexError, ValueError):
        mem_percent = "N/A (Non-Linux or permission error)"

    return {
        "cpu_usage_percent": round(cpu_usage, 1) if isinstance(cpu_usage, float) else cpu_usage,
        "memory_usage_percent": round(mem_percent, 1) if isinstance(mem_percent, float) else mem_percent
    }


# --- Placeholder Embedded Tools ---

def get_raspberry_pi_temp():
    """
    Placeholder for getting Raspberry Pi CPU temperature.
    In a real scenario, this would read from '/sys/class/thermal/thermal_zone0/temp'.
    """
    print("Reading mock Raspberry Pi temperature...")
    return 42.5

def set_gpio_pin(pin_number, state):
    """
    Placeholder for setting a GPIO pin state on a Raspberry Pi.
    In a real scenario, this would use a library like RPi.GPIO.
    """
    if not isinstance(pin_number, int) or not (0 <= pin_number <= 40):
        return "Error: Invalid pin number."
    if state not in [True, False]:
        return "Error: Invalid state, must be True or False."

    print(f"Setting GPIO pin {pin_number} to {'HIGH' if state else 'LOW'}")
    return f"Pin {pin_number} set to {state}"

# We can create a dictionary of all tools to make them easier to inject.
safe_tool_list = {
    "list_safe_directory": list_safe_directory,
    "get_system_stats": get_system_stats,
    "get_raspberry_pi_temp": get_raspberry_pi_temp,
    "set_gpio_pin": set_gpio_pin,
}
