from .coordinator.orchestrator import Orchestrator
from .executor.code_executor import execute_python_code

# ANSI escape codes for colors
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main_loop():
    """
    The main loop of the local interpreter.
    Connects all the components.
    """
    print(f"{colors.HEADER}{colors.BOLD}Welcome to Local Interpreter MVP{colors.ENDC}")
    print("Type 'exit' to quit.")

    orchestrator = Orchestrator()

    while True:
        try:
            user_input = input(f"{colors.BOLD}>>> {colors.ENDC}")
            if user_input.lower().strip() == 'exit':
                print(f"{colors.WARNING}Exiting...{colors.ENDC}")
                break

            # In a real app, you might have a debug flag for this.
            # For now, we've commented out the internal "thinking" process for a cleaner UI.
            # print(f"DEBUG: Passing to orchestrator: '{user_input}'")
            generated_code = orchestrator.process_user_input(user_input)

            output, success = execute_python_code(generated_code)

            print(f"{colors.OKBLUE}--- Result ---{colors.ENDC}")
            if success:
                # Pretty print for dictionaries or lists
                if output.strip().startswith(('{', '[')):
                     import json
                     try:
                         # Attempt to parse and pretty-print JSON-like strings
                         parsed = json.loads(output.replace("'", "\"")) # Allow single quotes
                         print(json.dumps(parsed, indent=2))
                     except json.JSONDecodeError:
                         print(output) # Fallback to raw print if not valid JSON
                else:
                    print(output)
            else:
                print(f"{colors.FAIL}An error occurred:\n{output}{colors.ENDC}")
            print(f"{colors.OKBLUE}--------------{colors.ENDC}\n")

        except KeyboardInterrupt:
            print(f"\n{colors.WARNING}Exiting...{colors.ENDC}")
            break
        except Exception as e:
            print(f"{colors.FAIL}A critical error occurred in the main loop: {e}{colors.ENDC}")
            break

if __name__ == '__main__':
    # We also need to refine the 'thinking' output from the other modules
    # for a truly clean run. For this MVP, we'll accept their print statements.
    main_loop()
