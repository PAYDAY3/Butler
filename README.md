# Butler (Formerly Jarvis) - An Intelligent Assistant System

Butler is a feature-rich intelligent assistant system developed in Python. It integrates natural language processing, a powerful algorithms library, and dynamic program management. Designed with a modular architecture, Butler is extensible through plugins and can perform various complex tasks via text or API commands.

This project includes a comprehensive library of common algorithms and exposes them through a developer-friendly REST API, making them accessible from any programming language.

# Butler (原 Jarvis) - 智能助手系统

Butler 是一个功能丰富的智能助手系统，基于 Python 开发。它集成了自然语言处理、一个强大的算法库和动态程序管理功能。Butler 采用模块化设计，支持插件扩展，能够通过文本或 API 指令执行各种复杂任务。

该项目包含一个全面的通用算法库，并通过对开发者友好的 REST API 将其开放，使其可以从任何编程语言中调用。

---

## Features / 主要功能

*   **Conversational AI**: Uses the DeepSeek API for natural language understanding and response generation.
*   **Extensible Program Management**: Dynamically loads and executes external program modules and plugins.
*   **Advanced Algorithm Library**: A rich, efficient, and well-documented library of algorithms for sorting, searching, text analysis, and more.
*   **Developer-Friendly API**: A dedicated REST API for direct access to the algorithm library, enabling integration with any language or platform.
*   **Interactive Command Panel**: A Tkinter-based GUI for text-based interaction.

*   **对话式AI**: 使用 DeepSeek API 进行自然语言理解和响应生成。
*   **可扩展的程序管理**: 动态加载和执行外部程序模块和插件。
*   **高级算法库**: 一个功能丰富、高效且文档齐全的算法库，用于排序、搜索、文本分析等。
*   **开发者友好的API**: 一个专用的 REST API，用于直接访问算法库，支持与任何语言或平台的集成。
*   **交互式命令面板**: 基于 Tkinter 的图形用户界面，用于文本交互。

---

## Getting Started / 开始使用

### Installation / 安装

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/PAYDAY3/Butler.git
    cd Butler
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    The project's dependencies are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Audio-related dependencies (`pyaudio`, `pyttsx3`, etc.) have been removed from the default requirements to ensure compatibility in environments without specific audio hardware/libraries. If you need voice features, you will need to install them separately and ensure your system has the required C libraries (e.g., `portaudio`).*

4.  **Configure API Keys:**
    Create a `.env` file in the root directory by copying the `.env.example` file. Then, add your API keys:
    ```
    DEEPSEEK_API_KEY="your_deepseek_api_key"
    AZURE_SPEECH_KEY="your_azure_speech_key"
    AZURE_SERVICE_REGION="your_azure_service_region"
    ```

---

## Algorithms Library / 算法库

The `butler.algorithms` module provides a collection of efficient, well-documented algorithms. You can use them in three primary ways:

`butler.algorithms` 模块提供了一系列高效且文档齐全的算法。您可以通过以下三种主要方式使用它们：

### 1. Via REST API (Recommended for All Languages) / 通过 REST API (推荐给所有语言)

For language-agnostic access, we provide a dedicated API server. This is the recommended way to use the algorithms from non-Python environments (e.g., Node.js, Java, Go) or from separate services.

为了实现与语言无关的访问，我们提供了一个专用的 API 服务器。这是从非 Python 环境（如 Node.js、Java、Go）或独立服务中使用这些算法的推荐方法。

**To start the server:**
**启动服务器:**
```bash
python -m butler.api
```
The server will run on `http://localhost:5001`.

**API Endpoints:**

*   **Sort / 排序**
    *   **Endpoint:** `POST /api/sort`
    *   **Body:** `{"numbers": [list_of_numbers], "algorithm": "quick_sort" | "merge_sort"}`
    *   **Example (`curl`):**
        ```bash
        curl -X POST -H "Content-Type: application/json" \
             -d '{"numbers": [5, 2, 8, 1, 9]}' \
             http://127.0.0.1:5001/api/sort
        ```
    *   **Response:** `{"sorted_numbers":[1,2,5,8,9]}`

*   **Binary Search / 二分查找**
    *   **Endpoint:** `POST /api/search`
    *   **Body:** `{"numbers": [sorted_list_of_numbers], "target": number}`
    *   **Example (`curl`):**
        ```bash
        curl -X POST -H "Content-Type: application/json" \
             -d '{"numbers": [1, 2, 5, 8, 9], "target": 8}' \
             http://127.0.0.1:5001/api/search
        ```
    *   **Response:** `{"index":3}`

*   **Fibonacci Number / 斐波那契数**
    *   **Endpoint:** `GET /api/fibonacci?n=<number>`
    *   **Example (`curl`):**
        ```bash
        curl http://127.0.0.1:5001/api/fibonacci?n=20
        ```
    *   **Response:** `{"n":20,"fibonacci_number":6765}`

*   **Text Cosine Similarity / 文本余弦相似度**
    *   **Endpoint:** `POST /api/text_similarity`
    *   **Body:** `{"text1": "string", "text2": "string"}`
    *   **Example (`curl`):**
        ```bash
        curl -X POST -H "Content-Type: application/json" \
             -d '{"text1": "hello world", "text2": "world hello there"}' \
             http://127.0.0.1:5001/api/text_similarity
        ```
    *   **Response:** `{"similarity":0.81...}`


### 2. As a Python Package / 作为 Python 包使用

The project is structured as an installable Python package. You can use the algorithms directly in your own Python code by importing them from the `butler.algorithms` module.

该项目被构建为一个可安装的 Python 包。您可以通过从 `butler.algorithms` 模块导入函数，在自己的 Python 代码中直接使用这些算法。

**Example:**
**示例:**
```python
from butler.algorithms import quick_sort, text_cosine_similarity

# Sort a list
my_list = [5, 2, 8, 1, 9]
sorted_list = quick_sort(my_list)
print(f"Sorted list: {sorted_list}")
# Output: Sorted list: [1, 2, 5, 8, 9]

# Calculate text similarity
similarity = text_cosine_similarity("The cat sat on the mat.", "A cat was sitting on the mat.")
print(f"Similarity: {similarity:.4f}")
# Output: Similarity: 0.8812
```

### 3. Via Conversational AI / 通过对话式AI

You can also interact with the algorithms using the main conversational assistant. This is suitable for interactive use or for high-level command-based integration.

您还可以使用主对话助手与算法进行交互。这适用于交互式使用或基于高级命令的集成。

**To start the assistant (with GUI):**
**启动助手 (带GUI):**
```bash
python -m butler.main
```

**To start the conversational API server:**
**启动对话式API服务器:**
```bash
python api_server.py
```
This server runs on `http://localhost:5000` and accepts commands in natural language.
该服务器运行在 `http://localhost:5000` 并接受自然语言命令。

**Example (`curl`):**
**示例 (`curl`):**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"command": "sort the numbers 5 2 8 1 9"}' \
     http://127.0.0.1:5000/api/command
```
**Response:** `{"response":"排序结果: [1, 2, 5, 8, 9]"}`

---

## Contribution / 贡献

We welcome contributions! Please feel free to submit a Pull Request. When contributing, please ensure your code adheres to the project's style and that you update documentation where appropriate.

我们欢迎任何贡献！请随时提交 Pull Request。在贡献时，请确保您的代码符合项目风格，并在适当时更新文档。

## License / 许可证

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
