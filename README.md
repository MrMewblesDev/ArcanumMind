# ArcanumMind

ArcanumMind is an intelligent Telegram bot engineered for performance and scalability. It leverages a fully asynchronous stack to deliver a responsive and engaging user experience. The bot's core functionality is to provide AI-powered conversations through Google's Gemini API, with a robust backend that ensures data persistence and clean architecture.

## 🏛️ Architecture

The project follows a clean, multi-layered architecture that separates concerns and enhances maintainability.

*   **Handlers (`/handlers`):** This layer is the entry point for user interactions. It receives commands and messages from Telegram, validates them, and passes the data to the appropriate services. It is responsible for user-facing messages and initial input processing.

*   **Services (`/services`):** The service layer contains the core business logic. It orchestrates the flow of data between the handlers and the data access layer (repositories). For example, the `gemini_service` is responsible for all interactions with the Gemini API.

*   **Repositories (`/repositories`):** This layer abstracts the database interactions. It implements the Repository Pattern, providing a clean API for the service layer to access and manipulate data without being coupled to the specific database implementation. This makes the application more modular and easier to test.

*   **Database (`database.py`):** Defines the SQLAlchemy ORM models (`User`, `Chat`, `Message`) and includes functions for database configuration, connection checking, and table creation.

*   **Middleware (`/middlewares`):** This layer intercepts incoming requests to perform cross-cutting concerns, such as managing the database session lifecycle for each update.

*   **Configuration (`config.py`):** Manages loading and validation of environment variables and application settings.

*   **Error Handling (`errors.py`):** Defines custom exception classes to provide more specific and meaningful error handling throughout the application.

## ✨ Features

*   **Fully Asynchronous:** Built with `aiogram` and `SQLAlchemy`'s async support for high concurrency.
*   **Repository Pattern:** Decouples business logic from data access, improving testability and maintainability.
*   **AI Integration:** Seamlessly integrates with the Google Gemini API for advanced conversational capabilities.
*   **Streaming Responses:** Provides a real-time feel by streaming AI responses to the user.
*   **Robust Error Handling:** Custom exceptions and a decorator-based error handler for database operations.
*   **Clean Code:** Follows modern Python best practices with clear separation of concerns.

## 🛠️ Tech Stack

*   **Framework:** `aiogram`
*   **Database:** `SQLAlchemy` with `aiosqlite`
*   **AI:** Google Gemini API via `google-generativeai`
*   **Configuration:** `python-dotenv`
*   **Language:** Python 3.9+

## ⚙️ Setup and Installation

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

## 🚀 Usage

To start the bot, run the `main.py` script:

```bash
python main.py
```

### Available Commands

*   `/start`: Initiates interaction with the bot and registers the user in the database.
*   `/help`: Displays a list of available commands and information about the bot.
*   `/ask <question>`: Asks a question to the AI. The AI does not have memory of previous questions in this mode.

## 📈 Future Enhancements

*   **Re-implement Multi-Chat Sessions:** Bring back persistent, context-aware conversations with the AI.
*   **Telegram Web Apps (TWA):** Integration of TWA for richer user interfaces and interactive elements.
*   **User Settings:** Implementation of user-specific settings (e.g., preferred AI model, language).
*   **Multi-language Support:** Full internationalization (i18n) to support multiple user languages.

## 🤝 Contributing

Contributions are welcome! If you have suggestions or want to improve the bot, please feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.