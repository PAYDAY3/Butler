from .interpreter import Interpreter

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
    The main command-line loop for interacting with the local interpreter.
    """
    print(f"{colors.HEADER}{colors.BOLD}Welcome to Local Interpreter CLI{colors.ENDC}")
    print("Type 'exit' to quit.")

    interpreter = Interpreter()
    if not interpreter.is_ready:
        print(f"{colors.FAIL}Interpreter could not be initialized. Exiting.{colors.ENDC}")
        return

    while True:
        try:
            user_input = input(f"{colors.BOLD}>>> {colors.ENDC}")
            if user_input.lower().strip() == 'exit':
                print(f"{colors.WARNING}Exiting...{colors.ENDC}")
                break

            result = interpreter.run(user_input)

            print(f"{colors.OKBLUE}--- Result ---{colors.ENDC}")
            print(result)
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
