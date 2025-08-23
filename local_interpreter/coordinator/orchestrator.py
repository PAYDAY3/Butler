import os
import re
import importlib
from openai import OpenAI
from ..tools.tool_decorator import TOOL_REGISTRY

def load_all_tools():
    """
    Dynamically imports all modules in the 'tools' directory to populate the TOOL_REGISTRY.
    This should be run once at startup.
    """
    tools_dir = os.path.dirname(__file__)
    tools_path = os.path.join(os.path.dirname(tools_dir), "tools")

    for filename in os.listdir(tools_path):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"local_interpreter.tools.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
            except Exception as e:
                print(f"Error loading tool module {module_name}: {e}")

def generate_system_prompt():
    """
    Generates the system prompt dynamically based on the registered tools.
    """
    prompt_header = """
You are a helpful assistant that translates natural language commands into executable Python code.
You have access to a set of safe tools to interact with the system.
"""

    tools_section = "**Available Tools:**\n"
    for tool_name, tool_data in TOOL_REGISTRY.items():
        tools_section += f"- `{tool_name}{tool_data['signature']}`: {tool_data['docstring']}\n"

    prompt_footer = """
**Instructions:**
- Choose the best tool for the job. For file operations, use the dedicated file tools.
- Only output the raw Python code to be executed. Do not add any explanation or formatting.
- Wrap the code in triple backticks (```python).
- If you cannot generate code for a command, output the word "Error" inside backticks.
"""
    return f"{prompt_header}\n{tools_section}\n{prompt_footer}"


class Orchestrator:
    def __init__(self):
        """
        Initializes the Orchestrator:
        1. Loads all available tools.
        2. Generates the system prompt.
        3. Sets up the Deepseek API client.
        """
        try:
            load_all_tools()
            self.system_prompt = generate_system_prompt()

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

        messages = [{"role": "system", "content": self.system_prompt}] + history

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
