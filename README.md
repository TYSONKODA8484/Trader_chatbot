# Trademate AI - Trading Assistant Web Application

## Overview

Trademate AI is an interactive web application designed to serve as your personal trading assistant. It empowers users to engage with a variety of powerful trading models, including Google Gemini, OpenAI GPT, and Anthropic Claude. This assistant excels at analyzing and responding to your trading-related queries, offering valuable insights, and even supporting file uploads (CSV, PDF, Image) for more in-depth analysis.

**Key Functionalities:**

* **Text-based communication with AI models:** Engage in natural language conversations with the integrated AI models.
* **File upload support:** Upload CSV, PDF, and image files for the AI to analyze and incorporate into its responses.
* **Seamless AI model switching:** Easily switch between Google Gemini, OpenAI GPT, and Anthropic Claude to leverage their unique strengths.
* **Flexible Backend:** Powered by Flask, providing a robust and scalable backend.
* **Versatile Frontends:** Offers two distinct frontend options: Streamlit for rapid prototyping and Bolt UI for a more customizable user interface.

## Table of Contents

* [Overview](#overview)
* [Backend Setup (Flask)](#backend-setup-flask)
* [Frontend Setup (Streamlit)](#frontend-setup-streamlit)
* [Frontend Setup (Bolt UI)](#frontend-setup-bolt-ui)
* [API Integration](#api-integration)
* [Running the Application](#running-the-application)
* [Environment Variables](#environment-variables)
* [Troubleshooting](#troubleshooting)

## Backend Setup (Flask)

This section outlines the steps to set up the Flask backend.

**Requirements:**

* Python 3.8 or higher

**Installation:**

1.  Navigate to the root directory of the project.
2.  Install the necessary dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```

**Environment Variables:**

1.  Create a `.env` file in the root directory of your project.
2.  Add your API keys to the `.env` file as follows:
    ```
    GEMINI_API_KEY=your_google_gemini_api_key
    OPENAI_API_KEY=your_openai_api_key
    CLAUDE_API_KEY=your_anthropic_claude_api_key
    ```
    **Important:** Ensure you replace `your_google_gemini_api_key`, `your_openai_api_key`, and `your_anthropic_claude_api_key` with your actual API keys.

**Running the Flask Backend:**

1.  Ensure that the `.env` file is correctly configured with your API keys.
2.  Execute the following command from the root directory to start the Flask backend:
    ```bash
    python main.py
    ```
3.  The Flask server will start and will be accessible by default at `http://127.0.0.1:5000`.

## Frontend Setup (Streamlit)

This section details how to set up and run the Streamlit user interface.

**Installation:**

1.  If you haven't already, install Streamlit using pip:
    ```bash
    pip install streamlit
    ```

**Running Streamlit UI:**

1.  Locate the Python file for your Streamlit application (e.g., `streamlit_app.py`).
2.  Open your terminal or command prompt, navigate to the directory containing this file.
3.  Run the Streamlit app using the following command:
    ```bash
    streamlit run streamlit_app.py
    ```
4.  Streamlit will automatically open a new tab in your web browser, displaying the Trademate AI frontend where you can begin interacting with the AI models.

## Frontend Setup (Bolt UI)

This section explains how to run the Bolt UI frontend.

**Running Bolt UI:**

1.  Ensure that the necessary frontend components (such as `ModelSelector`, `MessageList`, and `MessageInput`) are correctly linked to your Flask API endpoints. This typically involves configuring API request URLs within your Bolt UI code.
2.  Open your terminal or command prompt, navigate to the directory containing your Bolt UI project.
3.  Start the frontend using your package manager (usually npm or yarn):
    ```bash
    npm run start
    ```
    or
    ```bash
    yarn start
    ```
4.  Once the Bolt UI frontend is running, it will typically open in your web browser, allowing you to select different AI models and send messages to the backend.

## API Integration

The Flask backend serves as the central hub for handling communication between the frontends and the AI models. The frontends (Streamlit and Bolt UI) interact with the backend using the following API endpoints:

* **`POST /chat`:**
    * Purpose: Sends a user message and optionally includes files (CSV, PDF, Image) for the AI to analyze.
    * Request Body: Typically includes the user's message and potentially file data in a `multipart/form-data` format.
* **`POST /select_model`:**
    * Purpose: Sends the user's selection of the AI model (e.g., "Google Gemini", "OpenAI GPT", "Anthropic Claude") to the backend.
    * Request Body: Usually contains a JSON object with the selected model.
* **`POST /reset`:**
    * Purpose: Clears the current chat session and resets the chat history on the backend.
    * Request Body: Typically empty.

The frontend applications will need to implement logic to make these API requests to the Flask backend when users interact with the application (e.g., sending a message, selecting a model, or clicking a reset button).

## Running the Application

To run the complete Trademate AI application, you need to start both the backend and one of the frontends.

**Start Backend:**

1.  Open a terminal or command prompt.
2.  Navigate to the root directory of the project.
3.  Run the Flask backend:
    ```bash
    python main.py
    ```
    The backend will be running at `http://127.0.0.1:5000` by default.

**Start Frontend (Streamlit):**

1.  Open a new terminal or command prompt.
2.  Navigate to the directory containing your Streamlit application file (e.g., `streamlit_app.py`).
3.  Run the Streamlit frontend:
    ```bash
    streamlit run streamlit_app.py
    ```
    This will open the Streamlit UI in your browser.

**Start Frontend (Bolt UI):**

1.  Open a new terminal or command prompt.
2.  Navigate to the root directory of your Bolt UI project.
3.  Start the Bolt UI frontend using your package manager:
    ```bash
    npm run start
    ```
    or
    ```bash
    yarn start
    ```
    The Bolt UI will typically open in your browser.

## Environment Variables

The Trademate AI project relies on the following environment variables to securely manage API keys:

* `GEMINI_API_KEY`: Your unique API key for accessing the Google Gemini models.
* `OPENAI_API_KEY`: Your unique API key for accessing the OpenAI models (e.g., GPT).
* `CLAUDE_API_KEY`: Your unique API key for accessing the Anthropic Claude models.

## Troubleshooting

This section provides solutions to common issues you might encounter.

**Flask backend issues:**

* **Invalid API Keys:** Double-check your `.env` file to ensure that the API keys for Google Gemini, OpenAI, and Claude are correctly entered and are valid.
* **Server Not Running:** If the Flask server fails to start, examine the terminal output for any error messages. These messages might indicate missing dependencies (ensure you ran `pip install -r requirements.txt`) or issues with your Python environment.

**Frontend issues:**

* **Missing Frontend Dependencies:** For Streamlit, ensure you have it installed (`pip install streamlit`). For Bolt UI, make sure you have installed all necessary Node.js modules (run `npm install` or `yarn install` in your Bolt UI project directory).
* **No Response from Backend:** If the frontend is not receiving responses after sending messages or selecting models, verify the network connection between the frontend and the backend. Ensure that both the Flask backend and your chosen frontend are running and that the frontend is configured to communicate with the correct backend address (`http://127.0.0.1:5000` by default). Check your browser's developer console (usually accessed by pressing F12) for any network errors or JavaScript console errors.
