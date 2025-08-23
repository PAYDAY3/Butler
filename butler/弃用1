from flask import Flask, request, jsonify
from . import algorithms
import numpy as np
import os
import json

app = Flask(__name__)

# Helper to handle numpy arrays in JSON responses
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

app.json_encoder = NpEncoder

@app.route('/api/sort', methods=['POST'])
def sort_endpoint():
    """
    Endpoint for sorting a list of numbers.
    Expects JSON: {"numbers": [3, 1, 4], "algorithm": "quick_sort"}
    'algorithm' can be 'quick_sort' or 'merge_sort'.
    """
    data = request.get_json()
    if not data or "numbers" not in data:
        return jsonify({"error": "Missing 'numbers' in request"}), 400

    numbers = data['numbers']
    algo = data.get('algorithm', 'quick_sort') # Default to quick_sort

    if algo == 'quick_sort':
        result = algorithms.quick_sort(numbers)
    elif algo == 'merge_sort':
        result = algorithms.merge_sort(numbers)
    else:
        return jsonify({"error": f"Unknown sorting algorithm: {algo}"}), 400

    return jsonify({"sorted_numbers": result})

@app.route('/api/search', methods=['POST'])
def search_endpoint():
    """
    Endpoint for searching for a target in a sorted list.
    Expects JSON: {"numbers": [1, 2, 3, 4], "target": 3}
    """
    data = request.get_json()
    if not data or "numbers" not in data or "target" not in data:
        return jsonify({"error": "Missing 'numbers' or 'target' in request"}), 400

    # Binary search requires a sorted list
    numbers = sorted(data['numbers'])
    target = data['target']

    index = algorithms.binary_search(numbers, target)

    return jsonify({"index": index})

@app.route('/api/fibonacci', methods=['GET'])
def fibonacci_endpoint():
    """
    Endpoint for calculating a Fibonacci number.
    Expects query parameter: /api/fibonacci?n=10
    """
    n_str = request.args.get('n')
    if not n_str or not n_str.isdigit():
        return jsonify({"error": "Query parameter 'n' must be a positive integer."}), 400

    n = int(n_str)
    result = algorithms.fibonacci(n)

    return jsonify({"n": n, "fibonacci_number": result})

@app.route('/api/text_similarity', methods=['POST'])
def text_similarity_endpoint():
    """
    Endpoint for calculating cosine similarity between two texts.
    Expects JSON: {"text1": "hello world", "text2": "world hello"}
    """
    data = request.get_json()
    if not data or "text1" not in data or "text2" not in data:
        return jsonify({"error": "Missing 'text1' or 'text2' in request"}), 400

    similarity = algorithms.text_cosine_similarity(data['text1'], data['text2'])

    return jsonify({"similarity": similarity})

# Note: Image processing and pathfinding are more complex to handle in a simple API.
# - Edge detection would require file uploads (e.g., multipart/form-data).
# - A* pathfinding requires a graph and a heuristic function, which are not easily JSON-serializable.
# These are omitted for now to keep the API focused and clean, but can be added later if needed.

def run_algo_api_server():
    # Running in debug mode is not recommended for production
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == '__main__':
    run_algo_api_server()
