import threading
from flask import Flask, request, jsonify
from butler.main import Jarvis

# --- Monkey-Patching Setup ---
# This list will hold the response from the monkey-patched speak method.
# It's a simple way to communicate between the Flask thread and the Jarvis thread.
captured_responses = []

# Keep a reference to the original method
original_speak = Jarvis.speak

def api_speak(self, audio):
    """
    This function will replace the original Jarvis.speak method.
    Instead of playing audio, it captures the response text.
    """
    # The original ui_print is useful for logging in the console where the API server is running.
    self.ui_print(f"Jarvis (API): {audio}")
    captured_responses.append(audio)
    # We skip the audio generation and playback parts of the original speak method.

# Apply the patch
Jarvis.speak = api_speak
# --- End of Monkey-Patching Setup ---


# --- Jarvis Instance Setup ---
# We need to run Jarvis in headless mode, so we pass root=None.
# The program_mapping is needed for the CommandPanel, but we can pass an empty dict.
# We need to load the programs for the handler to work.
print("Initializing Jarvis for API...")
jarvis_instance = Jarvis(root=None)
# The `open_programs` method is called inside `panel_command_handler`,
# but we will call `handle_user_command` directly.
# Let's load the programs once at the start.
# The `program_folder` argument should be a string.
programs = jarvis_instance.open_programs("./package")
print("Jarvis initialized.")
# --- End of Jarvis Instance Setup ---


# --- Flask App Setup ---
app = Flask(__name__)

@app.route('/api/command', methods=['POST'])
def process_command():
    """
    API endpoint to process a user command.
    """
    if not request.json or 'command' not in request.json:
        return jsonify({"error": "Missing 'command' in request body"}), 400

    command = request.json['command']

    # Clear previous responses and process the new command.
    captured_responses.clear()
    jarvis_instance.handle_user_command(command, programs)

    # Get the last response captured by our patched speak method.
    response_text = captured_responses[-1] if captured_responses else "No response from assistant."

    return jsonify({"response": response_text})

def run_api_server():
    # Running in debug mode is not recommended for production
    # but is fine for this context.
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    run_api_server()
