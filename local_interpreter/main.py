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
    Connects all the components and maintains conversation history.
    """
    print(f"{colors.HEADER}{colors.BOLD}Welcome to Local Interpreter{colors.ENDC}")
    print("Type 'exit' to quit.")

    orchestrator = Orchestrator()
    conversation_history = []

    while True:
        try:
            user_input = input(f"{colors.BOLD}>>> {colors.ENDC}")
            if user_input.lower().strip() == 'exit':
                print(f"{colors.WARNING}Exiting...{colors.ENDC}")
                break

            # Append the user's message to the history
            conversation_history.append({"role": "user", "content": user_input})

            generated_code = orchestrator.process_user_input(conversation_history)

            # Optional: Display the code that is about to be run
            print(f"{colors.OKCYAN}Running code:\n---\n{generated_code}\n---{colors.ENDC}")

            output, success = execute_python_code(generated_code)

            print(f"{colors.OKBLUE}--- Result ---{colors.ENDC}")
            if success:
                print(output)
            else:
                print(f"{colors.FAIL}An error occurred:\n{output}{colors.ENDC}")
            print(f"{colors.OKBLUE}--------------{colors.ENDC}\n")

            # Append the assistant's response (the code and its output) to the history
            # This helps the model understand the result of its previous actions
            assistant_response = f"Executed Code:\n```python\n{generated_code}```\nOutput:\n```\n{output}```"
            conversation_history.append({"role": "assistant", "content": assistant_response})

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
