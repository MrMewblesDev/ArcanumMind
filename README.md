# ArcanumMind

## Project Overview

ArcanumMind is an intelligent Telegram bot designed to assist users with various tasks, provide information, and engage in dynamic, context-aware conversations powered by advanced Artificial Intelligence. The bot aims to offer a personalized and helpful experience, leveraging persistent data storage to maintain user and chat context across sessions.

## Features

*   **AI-Powered Conversations:** Engage in natural language conversations with the bot, powered by the Google Gemini API.
*   **Persistent Chat History:** All chat interactions are stored in a SQLite database, allowing for continuous and context-aware dialogues.
*   **User Management:** Tracks individual users, enabling personalized experiences and settings.
*   **Multi-Chat Support:** Manages multiple chat sessions for each user, allowing for different conversation contexts.
*   **Scalable Database:** Utilizes a normalized SQLite schema for efficient and robust data management of users, chats, and messages.
*   **Message Chunking:** Automatically splits long AI responses into smaller messages to comply with Telegram's message length limits.
*   **Logging:** Implemented logging for improved error tracking and debugging.


## Technologies Used

*   **Python:** The core programming language for the bot's logic.
*   **`python-telegram-bot`:** A powerful and easy-to-use library for interacting with the Telegram Bot API.
*   **Google Gemini API:** Provides the advanced AI capabilities for generating responses.
*   **SQLite:** A lightweight, file-based relational database for persistent data storage.
*   **`python-dotenv`:** For managing environment variables (API keys, tokens).
*   **`re` (Regular Expressions):** Used for advanced text processing, such as message chunking.

## Setup and Installation

Follow these steps to get ArcanumMind up and running on your local machine.

### Prerequisites

*   Python 3.9+
*   `pip` (Python package installer)
*   `git` (for cloning the repository)

### 1. Clone the Repository

```bash
git clone https://github.com/MrMewblesDev/ArcanumMind
cd ArcanumMind
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the project and add your Telegram Bot Token and Google Gemini API Key:

```
TOKEN=YOUR_TELEGRAM_BOT_TOKEN
GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY
GEMINI_MODEL=YOUR_GEMINI_MODEL
LOG_LEVEL=YOUR_LOG_LEVEL
```
*   **`TOKEN`** [REQUIRED]: Obtain this from BotFather on Telegram.
*   **`GEMINI_API_KEY`** [REQUIRED]: Get this from the Google AI Studio.
*   **`GEMINI_MODEL`**: Choose your preferable gemini model, defaults to gemini-2.5-pro if not set (See [gemini models](https://ai.google.dev/gemini-api/docs/models)). **This bot supports only text output models right now!**
*   **`LOG_LEVEL`**: Choose your preferable logging priority, defaults to INFO if not set.

### 5. Initialize the Database

The bot uses SQLite for data storage. Run the `database.py` script once to create the necessary tables:

```bash
python database.py
```
This will create a `bot_database.db` file in your project directory.

## Usage

To start the bot, run the `main.py` script:

```bash
python main.py
```

### Available Commands

*   `/start`: Initiates interaction with the bot and registers the user.
*   `/help`: Displays a list of available commands and information about the bot.
*   `/new_ai_chat`: Starts a new conversation session with the AI.
*   `/stop_ai_chat`: Ends the current AI conversation session.

## Future Enhancements

*   **Telegram Web Apps (TWA):** Integration of TWA for richer user interfaces and interactive elements.
*   **User Settings:** Implementation of user-specific settings (e.g., preferred AI model, language, tone).
*   **Multi-language Support:** Full internationalization (i18n) to support multiple user languages.

## Contributing

Contributions are welcome! If you have suggestions or want to improve the bot, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
