import telebot
from telebot.types import BotCommand
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted
import os
from dotenv import load_dotenv
import re
import database as db
import logging

# Load environment variables from a .env file
load_dotenv()
# Dictionary to store user contexts for active AI chats.
# user_contexts = {} # Currently is going to be replaced with database storage.

def setup_logging():
    """
    Sets up logging for the application.
    """
    # Get log level from environment variable, default to INFO if not set
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Set up logging configuration
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    logging.info("Logging is set up.")
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.info("urllib3.connectionpool logging level set to WARNING to prevent API key leakage.")

setup_logging()

def setup_bot():
    """
    Sets up the Telegram bot using the API token from environment variables.
    """

    logging.info("Bot setup is initializing...")

    TOKEN = os.getenv("TOKEN")
    # Checks if the token is set; if not - program exits. 
    if not TOKEN:
        logging.error("Error: The 'TOKEN' environment variable is not set.")
        exit(1)
    # Initializes the bot.
    try:
        bot = telebot.TeleBot(TOKEN)
        logging.info("Bot is initialized successfully.")
        return bot
    except telebot.TeleBotException as e:
        logging.error(f"Error initializing the bot: {e}")
        exit(1)
    
def setup_ai():
    """
    Sets up the Gemini AI model using the API key from environment variables.
    """

    logging.info("Gemini model is initializing...")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")  # Default model if not specified

    # Checks if the Gemini API key is set; if not, AI functionality will be unavailable. 
    if not GEMINI_API_KEY:
        logging.error("Error: The 'GEMINI_API_KEY' environment variable is not set.")
    else:
        try: 
            genai.configure(api_key=GEMINI_API_KEY)

            model = genai.GenerativeModel(GEMINI_MODEL) # Uses the model specified in the environment variable

            logging.info("Gemini model is initialized successfully.")
            return model
        except GoogleAPIError as e:
            logging.error(f"Error initializing the AI model: {e}")

def setup_bot_commands(bot):
    """
    Sets up the bot commands that will be visible in the Telegram interface.

    Args:
        bot (telebot.TeleBot): The Telegram bot instance.
    """
    logging.info("Setting up bot commands...")

    commands = [
        BotCommand("start", "Начать диалог с ботом"),
        BotCommand("help", "Получить помощь и информацию о боте"),
        BotCommand("new_ai_chat", "Начать новый чат с ИИ"),
        BotCommand("stop_ai_chat", "Остановить все активные чаты с ИИ"),
        BotCommand("list_chats", "Показать все чаты с ИИ"),
    ]

    try:
        bot.set_my_commands(commands)
        logging.info("Successfully set bot commands.")
    except telebot.apihelper.ApiException as e:
        logging.error(f"Error setting bot commands: {e}")

bot = setup_bot()
setup_bot_commands(bot)
model = setup_ai()

def generate_gemini_response(prompt: str) -> str | None:
    """
    Generates a response from the Gemini AI model based on the provided prompt.

    Args:
        prompt (str): The input prompt for the AI model.

    Returns:
        str | None: The generated response from the AI model, or None if an error occurs.
    """

    if not model:
        logging.error("Error: Gemini model is not initialized.")
        return None
    
    try: 
        response = model.generate_content(prompt)
        return response.text
    except ResourceExhausted as e:
        logging.error(f"Resource exhausted error from AI model: {e}")
        return "Извините, но в данный момент сервис ИИ недоступен из-за превышения квоты. Пожалуйста, попробуйте позже."
    except GoogleAPIError as e:
        logging.error(f"Error generating response from AI model: {e}")
        return None

def get_or_create_user_db_id(telegram_id: int) -> int | None:
    """
    Retrieves the internal database ID for a user based on their Telegram ID.

    If the user does not exist in the database, they are added.

    Args:
        telegram_id (int): The unique Telegram ID of the user.

    Returns:
        int | None: The internal database ID of the user, or None if an error occurs.
    """
    logging.info(f"Retrieving or creating user with Telegram ID {telegram_id}...")

    user_db_id = db.get_user_db_id(telegram_id)

    if user_db_id is not None:
        logging.info(f"Successfully retrieved DB ID {user_db_id} for Telegram ID {telegram_id}.")
        return user_db_id
    else:
        logging.error(f"Failed to get or create user with Telegram ID {telegram_id}. See previous logs for details.")
        return None

@bot.message_handler(commands=['start'])
def main(message):

    logging.info(f"Received /start command from user ID {message.from_user.id}.")
    # message - contains information about user and chat
    # this function is called every time "/start" is used
    # parse_mode is used for html tag. 

    bot.send_message(message.chat.id, "<b>Привет</b>! Меня зовут <u>ArcanumMind</u> (сокращенно Арканум). \nВведи /help для большей информации.", parse_mode="html")
    logging.info(f"Successfully handled /start command for user ID {message.from_user.id}.")
    
@bot.message_handler(commands=['help'])
def help(message):
    logging.info(f"Received /help command from user ID {message.from_user.id}.")
    # This function is called every time "/help" is used
    # parse_mode is used for html tag.
    bot.reply_to(message, "Я ArcanumMind, ваш ИИ-помощник (сокращенно Арканум). Моя цель — помогать вам с информацией, отвечать на вопросы и поддерживать увлекательные диалоги. Я здесь, чтобы сделать ваше взаимодействие с ИИ максимально продуктивным и приятным.\n"
                          "Доступные команды:\n"
                          "/start - начать диалог\n"
                          "/help - получить помощь\n"
                          "/new_ai_chat - начать чат с ИИ\n"
                          "/stop_ai_chat - остановить чат с ИИ\n"
                          "/list_chats - показать все чаты с ИИ\n", parse_mode="html")
    logging.info(f"Successfully handled /help command for user ID {message.from_user.id}.")


@bot.message_handler(commands=['new_ai_chat'])
def start_ai_chat(message):
    logging.info(f"Creating new AI chat for user ID {message.from_user.id}...")
    # Get user's internal database ID for further operations
    user_id = message.from_user.id
    user_db_id = get_or_create_user_db_id(user_id)

    # Check if user_db_id is valid and handle the error if not
    if user_db_id is None:
        bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
        logging.error(f"Error: Unable to retrieve or create user with Telegram ID {user_id}.", exc_info=True)
    else:
        # Check if user already has an active chat. If yes, inform them and
        active_chat_id = db.get_active_chat_id(user_db_id)
        if active_chat_id is None:
            bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
            logging.error(f"Error: Unable to check active chats for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)
            return
        elif active_chat_id:
            logging.debug(f"Aborting new chat creation: User ID {user_id} (DB ID: {user_db_id}) already has an active chat.")
            bot.reply_to(message, "У вас уже есть активный чат с ИИ. Пожалуйста, завершите его перед началом нового воспользовавшись командой /stop_ai_chat.")
            return
        # If no, create a new chat and inform them.
        # Add a new chat for the user in the database. 
        # Currently, chat_name is hardcoded, should be fixed later.
        chat_name = "Chat with AI"
        new_chat_id = db.add_new_chat(user_db_id, chat_name, True)
        if new_chat_id:
            bot.reply_to(message, "Вы начали новый чат с ИИ. Теперь вы можете задавать вопросы ИИ.")
            logging.info(f"Function add_new_chat executed for user ID {user_id} (DB ID: {user_db_id}).")
        else:
            bot.reply_to(message, "Произошла ошибка при создании нового чата. Пожалуйста, попробуйте снова позже.")
            logging.error(f"Error: Unable to create new chat for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)

@bot.message_handler(commands=['stop_ai_chat'])
def stop_ai_chat(message):
    # Get user's internal database ID for further operations
    user_id = message.from_user.id
    user_db_id = get_or_create_user_db_id(user_id)
    # Check if user_db_id is valid and handle the error if not
    if user_db_id is None:
        bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
        logging.error(f"Error: Unable to retrieve or create user with Telegram ID {user_id}.", exc_info=True)
    else:
        active_chat_id = db.get_active_chat_id(user_db_id)
        if active_chat_id is None:
            bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
            logging.error(f"Error: Unable to check active chats for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)
            return
        elif not active_chat_id:
            logging.debug(f"Aborting chat deactivation: User ID {user_id} (DB ID: {user_db_id}) has no active chats.")
            bot.reply_to(message, "У вас нет активных чатов с ИИ. Пожалуйста, начните новый чат с помощью команды /new_ai_chat.")
            return
        else:
            db.deactivate_all_user_chats(user_db_id)
            bot.reply_to(message, "Вы остановили все активные чаты с ИИ.")
            logging.info(f"Function deactivate_all_user_chats executed for user ID {user_id} (DB ID: {user_db_id}).")

@bot.message_handler(commands=['list_chats'])
def list_chats(message):

    # Get user's internal database ID for further operations
    user_id = message.from_user.id
    user_db_id = get_or_create_user_db_id(user_id)
    # Check if user_db_id is valid and handle the error if not
    if user_db_id is None:
        bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
        logging.error(f"Error: Unable to retrieve or create user with Telegram ID {user_id}.", exc_info=True)
    else:
        logging.info(f"Fetching chats for user ID {user_id} (DB ID: {user_db_id})...")

        chats = db.get_user_chats(user_db_id)
        if chats:
            response = "Ваши чаты:\n"
            for chat in chats:
                response += f"ID: {chat['id']}, Название: {chat['chat_name']}, Время создания: {chat['created_at']}, Активен: {'Да' if chat['is_active'] else 'Нет'}\n"
            bot.reply_to(message, response)
        elif chats is None:
            bot.reply_to(message, "Произошла ошибка при получении списка чатов. Пожалуйста, попробуйте снова позже.")
            logging.error(f"Error: Unable to fetch chats for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)
        else:
            bot.reply_to(message, "У вас нет сохраненных чатов.")

# This function is handling every message bot receives that didn't match any previous commands.
@bot.message_handler(func=lambda message: True)
def echo_all(message):

    logging.info(f"Initiating message handling for user ID {message.from_user.id}...")
    user_id = message.from_user.id
    user_db_id = get_or_create_user_db_id(user_id)

    # Check if user_db_id is valid and handle the error if not
    if user_db_id is None:
        bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
        logging.error(f"Error: Unable to retrieve or create user with Telegram ID {user_id}.", exc_info=True)
        return
    # Now user is guaranteed to be in the database.
    # Check if user has an active chat. If not, inform them that such command doesn't exist.
    active_chat_id = db.get_active_chat_id(user_db_id)

    if active_chat_id is None:
        bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
        logging.error(f"Error: Unable to check active chats for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)
        return
    elif not active_chat_id:
        bot.reply_to(message, "Такой команды нет. Пожалуйста, используйте /help для списка доступных команд. \nЕсли вы хотите начать чат с ИИ, используйте команду /new_ai_chat.")
        logging.info(f"Successfully handled non-command message for user ID {user_id} (DB ID: {user_db_id}) without active chat.")
        return
    else:
        # User has an active chat, proceed with AI response generation using database context.
        logging.info(f"User ID {user_id} (DB ID: {user_db_id}) has an active chat. Proceeding with AI response generation.")
        # Get user message and adding it into chat history.
        user_message = message.text

        chat_id = db.get_active_chat_id(user_db_id)
        # it should never be 0 here, but just in case we check it. 
        # We don't use "if..elif..else" here because it's easier to read next code this way.
        if chat_id is None:
            bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
            logging.error(f"Error: Unable to fetch active chat ID for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)
            return
        if not chat_id:
            bot.reply_to(message, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
            logging.error(f"Error: No active chat found for user ID {user_id} despite earlier check (DB ID: {user_db_id}).", exc_info=True)
            return
        
        db.add_message_to_chat(chat_id, role="user", content=user_message)
        # Fetch the entire chat history for context.
        chat_history = db.get_chat_history(chat_id)

        if chat_history is None:
            bot.reply_to(message, "Произошла ошибка при получении истории чата. Пожалуйста, попробуйте снова позже.")
            logging.error(f"Error: Unable to fetch chat history for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)
            return
        else:
            # Construct the prompt for the AI model using chat history.
            prompt = ""
            for msg in chat_history:
                if msg['role'] == 'user':
                    role = "User"
                elif msg['role'] == 'assistant':
                    role = "AI"
                else:
                    role = "System"
                
                # Optional: include timestamps in the prompt based on environment variable
                show_time_in_prompt = os.getenv("SHOW_TIME_IN_PROMPT", False).lower()
                if show_time_in_prompt:
                    prompt += f"[{msg['created_at']}] {role}: {msg['content']}\n"
                else:
                    prompt += f"{role}: {msg['content']}\n"

            logging.debug(f"Constructed assistant prompt for user ID {user_id} (DB ID: {user_db_id}): {prompt}")

            ai_response = ask_gemini(prompt)

            if ai_response is None:
                bot.reply_to(message, "Произошла ошибка при генерации ответа ИИ. Пожалуйста, попробуйте снова позже.")
                logging.error(f"Error: AI response generation failed for user ID {user_id} (DB ID: {user_db_id}).", exc_info=True)
                return
            else:
                # Add AI response to chat history in the database.
                db.add_message_to_chat(chat_id, role="assistant", content=ai_response)
                logging.info(f"AI response generated and added to chat history for user ID {user_id} (DB ID: {user_db_id}).")

                # Split the AI response into manageable chunks for Telegram
                response_chunks = split_message(ai_response)

                for chunk in response_chunks:
                    bot.send_message(message.chat.id, chunk)
                logging.info(f"Successfully sent AI response to user ID {user_id} (DB ID: {user_db_id}).")
                return


def split_message(text, chunk_size=4000):
    """
    Splits a long text into chunks for sending via Telegram.

    This function takes a long text and breaks it into several parts (chunks)
    so that they can be sent to Telegram, as Telegram has a limit on the length
    of a single message. The splitting occurs by sentences to avoid
    breaking sentences in the middle.

    Args:
        text (str): The original text to split.
        chunk_size (int, optional): The maximum chunk size. Defaults to 4000 characters.
                                    This value is chosen because Telegram's limit is 4096 characters,
                                    leaving a small buffer.

    Returns:
        list[str]: A list of text chunks. Each chunk is a string
                     that does not exceed chunk_size in length.
    """
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    current_chunk = ""
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def ask_gemini(prompt: str) -> None | str:
    logging.info("Generating AI response using Gemini model...")
    if not model:
        logging.error("Error: Gemini model is not initialized.")
        return None
    else:
        return generate_gemini_response(prompt)

if __name__ == "__main__":

    # Initializing the database before starting the bot
    logging.info("Database is initializing...")
    db.initialize_db()
    logging.info("Database is ready.")

    # The bot should not stop; it must keep running. 
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Error: {e}")

