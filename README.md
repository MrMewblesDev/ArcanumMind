# ArcanumMind

## Project Overview

ArcanumMind is an intelligent Telegram bot designed to assist users with various tasks, provide information, and engage in dynamic, context-aware conversations powered by advanced Artificial Intelligence. The bot aims to offer a personalized and helpful experience, leveraging persistent data storage to maintain user context across sessions.

## 🚀 Architectural Upgrade Complete

**Please note:** This project has recently undergone a major architectural migration from a synchronous stack (`pyTelegramBotAPI`, `sqlite3`) to a fully asynchronous stack (`aiogram 3`, `SQLAlchemy`). This significantly improves performance, scalability, and maintainability.

## Features

*   **Asynchronous by Design:** Built on `aiogram`, the bot can handle many concurrent users efficiently without blocking.
*   **AI-Powered Conversations:** Engage in natural language conversations with the bot, powered by the Google Gemini API with real-time streaming responses.
*   **Persistent User Management:** User data is stored in a database, allowing the bot to recognize users and provide a continuous experience.
*   **Robust Database Layer:** Uses `SQLAlchemy 2.0` ORM for type-safe, asynchronous, and reliable database interactions.
*   **Middleware-Driven:** A database session middleware cleanly manages the lifecycle of database connections for each incoming request.
*   **Message Chunking:** Automatically splits long AI responses into smaller messages to comply with Telegram's message length limits.
*   **Structured Logging:** Implemented comprehensive logging for improved error tracking and debugging.

## Technologies Used

*   **Python:** The core programming language for the bot's logic.
*   **`aiogram`:** A modern, powerful, and fully asynchronous framework for building Telegram bots.
*   **`SQLAlchemy`:** A comprehensive SQL toolkit and Object-Relational Mapper (ORM) for database interactions.
*   **`aiosqlite`:** An asynchronous driver for SQLite, used by SQLAlchemy.
*   **Google Gemini API:** Provides the advanced AI capabilities for generating responses.
*   **`python-dotenv`:** For managing environment variables (API keys, tokens).
*   **`re` (Regular Expressions):** Used for advanced text processing, such as intelligent message chunking.

## Setup and Installation

Follow these steps to get ArcanumMind up and running on your local machine.

### Prerequisites

*   Python 3.9+
*   `pip` (Python package installer)
*   `git` (for cloning the repository)

### 1. Clone the Repository

```bash
git clone https://github.com/MrMewblesDev/ArcanumMind
cd ArcanumMind```

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

Create a `.env` file in the root directory of the project and add your Telegram Bot Token and other configuration details:

```
BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
GEMINI_MODEL="gemini-2.5-flash"
LOG_LEVEL="INFO"
DB_URL="sqlite+aiosqlite:///./arcanum.db"
```
*   **`BOT_TOKEN`** [REQUIRED]: Obtain this from BotFather on Telegram.
*   **`GEMINI_API_KEY`** [REQUIRED]: Get this from the Google AI Studio.
*   **`GEMINI_MODEL`**: The specific text-generation model to use (see [gemini models](https://ai.google.dev/gemini-api/docs/models)).
*   **`LOG_LEVEL`**: The logging priority (e.g., DEBUG, INFO, WARNING, ERROR). Defaults to `INFO`.
*   **`DB_URL`**: The connection string for the database. Defaults to a local SQLite file.

### 5. Database Initialization

**This step is now automatic!** The bot will create the database and tables on its first startup, so no manual script execution is needed.

## Usage

To start the bot, run the `main.py` script:

```bash
python main.py
```

### Available Commands

*   `/start`: Initiates interaction with the bot and registers the user in the database.
*   `/help`: Displays a list of available commands and information about the bot.
*   `/ask <question>`: Asks a question to the AI. The AI does not have memory of previous questions in this mode.

## Future Enhancements

*   **Re-implement Multi-Chat Sessions:** Bring back persistent, context-aware conversations with the AI.
*   **Telegram Web Apps (TWA):** Integration of TWA for richer user interfaces and interactive elements.
*   **User Settings:** Implementation of user-specific settings (e.g., preferred AI model, language).
*   **Multi-language Support:** Full internationalization (i18n) to support multiple user languages.

## Contributing

Contributions are welcome! If you have suggestions or want to improve the bot, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.