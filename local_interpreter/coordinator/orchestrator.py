import os
import re
from openai import OpenAI

# System prompt to guide the LLM
SYSTEM_PROMPT = """
You are a helpful assistant that translates natural language commands into executable Python code.
You have access to a set of safe tools and the ability to execute shell commands.

- To execute a shell command, use the `run_shell("your command")` function.
- For other tasks, write standard Python code.
- Only output the raw code to be executed, without any explanation or formatting.
- Wrap the code in triple backticks (```).
- If you cannot generate code for a command, output the word "Error" inside backticks.

Example:
User: list files in the current directory
Assistant:
```
print(run_shell("ls -l"))
```
"""

class Orchestrator:
    def __init__(self):
        """
        Initializes the Orchestrator by setting up the Deepseek API client.
        """
        try:
            # It's better to load the API key from environment variables
            # The user should have a .env file based on the main README
            from dotenv import load_dotenv
            load_dotenv()
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        except Exception as e:
            print(f"Error initializing Orchestrator: {e}")
            self.client = None

    def process_user_input(self, history: list) -> str:
        """
        Takes the conversation history, sends it to the Deepseek LLM to generate Python code,
        and returns the code to be executed.
        """
        if not self.client:
            return 'print("Orchestrator not initialized. Please check API key.")'

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        try:
            response = self.client.chat.completions.create(
                model="deepseek-coder",
                messages=messages,
                max_tokens=500,
                temperature=0,
            )

            generated_text = response.choices[0].message.content

            # Extract code from within the triple backticks
            match = re.search(r"```(python\n)?(.*?)```", generated_text, re.DOTALL)
            if match:
                return match.group(2).strip()

            # Fallback for models that might not use backticks as instructed
            if "run_shell" in generated_text or "print" in generated_text:
                return generated_text.strip()

            return 'print("Error: Could not generate valid code from the response.")'

        except Exception as e:
            print(f"Error calling Deepseek API: {e}")
            return f'print("Error during code generation: {e}")'
