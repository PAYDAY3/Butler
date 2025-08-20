# Butler (Jarvis) Deployment Guide

This guide provides instructions for setting up and running the Butler (formerly Jarvis) voice assistant application from source. This project has several complex dependencies, so please follow the steps carefully.

## 1. Prerequisites

Before you begin, ensure your system meets the following requirements.

### System-level Dependencies
You must have the following software installed on your system:

1.  **Python**: Version 3.8 or newer.
2.  **PortAudio**: This is required to compile the `pyaudio` library.
    -   On Debian/Ubuntu: `sudo apt-get update && sudo apt-get install portaudio19-dev`
    -   On other systems, please use your system's package manager to install the PortAudio development package.
3.  **Redis**: The web crawler functionality depends on a Redis server.
    -   Install Redis and ensure it is running on the default port: `localhost:6379`.
    -   On Debian/Ubuntu: `sudo apt-get install redis-server`

### Manual Python Dependencies

There are no manual Python dependencies anymore.

## 2. Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Install Other Python Dependencies**
    Install all other required Python libraries from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the Butler Application**
    Install the application itself in editable mode. This will make the `butler` command available in your shell.
    ```bash
    pip install .
    ```

## 3. Configuration

The application requires API keys for its core services.

1.  **Create `.env` file**: Copy the example template to a new file named `.env`.
    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env` file**: Open the `.env` file in a text editor and fill in your secret keys:
    ```dotenv
    # DeepSeek API Key for NLP processing
    DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY_HERE

    # Azure Cognitive Speech Services for speech-to-text
    AZURE_SPEECH_KEY=YOUR_AZURE_SPEECH_KEY_HERE
    AZURE_SERVICE_REGION=chinaeast2
    ```

## 4. Data Files

The application requires a custom data file to be placed in the `butler/` package directory.

1.  **Startup Sound**: Place your desired startup sound effect file inside the `butler/resources/` directory. The application looks for `butler/resources/jarvis.wav`.

## 5. Running the Application

Once all the steps above are completed, you can run the application by simply typing the following command in your terminal:
```bash
butler
```
The application will start, and you can interact with it through the GUI.

## 6. Building a Standalone Executable (Advanced)

It is possible to build a standalone executable using `PyInstaller`. This guide has prepared the project structure for this. The basic command is:
```bash
pyinstaller --name Butler --onefile --add-data "butler/resources:butler/resources" butler/main.py
```
**Note**: Before running this, you must ensure that the required data files (as described in Section 4) are already in place. The executable will be created in the `dist` directory.
