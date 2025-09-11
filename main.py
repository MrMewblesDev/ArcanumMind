import telebot
from telebot.types import BotCommand
import google.generativeai as genai
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
        except genai.Error as e:
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
    except telebot.TeleBotException as e:
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
    except genai.Error as e:
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

    # Add user to our database if it doesn't exist yet
    user_id = message.from_user.id
    get_or_create_user_db_id(user_id)
    user_db_id = get_or_create_user_db_id(user_id)
    if user_db_id is None:
        bot.send_message(message.chat.id, "Произошла ошибка при работе с базой данных. Пожалуйста, попробуйте снова позже.")
        logging.error(f"Error: Unable to retrieve or create user with Telegram ID {user_id}.", exc_info=True)
        return
    # Now user is guaranteed to be in the database.

    # message - contains information about user and chat
    # this function is called every time "/start" is used
    # parse_mode is used for html tag. 

    bot.send_message(message.chat.id, "<b>Привет</b>! Меня зовут <u>ArcanumMind</u> (сокращенно Арканум). \nВведи /help для большей информации.", parse_mode="html")

    
@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Я ArcanumMind, ваш ИИ-помощник (сокращенно Арканум). Моя цель — помогать вам с информацией, отвечать на вопросы и поддерживать увлекательные диалоги. Я здесь, чтобы сделать ваше взаимодействие с ИИ максимально продуктивным и приятным.\n"
                          "Доступные команды:\n"
                          "/start - начать диалог\n"
                          "/help - получить помощь\n"
                          "/new_ai_chat - начать чат с ИИ\n"
                          "/stop_ai_chat - остановить чат с ИИ\n"
                          "/list_chats - показать все чаты с ИИ\n", parse_mode="html")


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
        if db.user_has_active_chat(user_db_id):
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
        if not db.user_has_active_chat(user_db_id):
            logging.debug(f"Aborting chat deactivation: User ID {user_id} (DB ID: {user_db_id}) has no active chats.")
            bot.reply_to(message, "У вас нет активных чатов с ИИ. Пожалуйста, начните новый чат с помощью команды /new_ai_chat.")
            return

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
# Currently is under development and is commented out.
# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
    # chatid = message.chat.id # Gets unique chat id

    # user_message_text = message.text # Gets user's message

    # if chatid in user_contexts: # Check if user has chat with AI right now

    #     chat_history = user_contexts[chatid] # Loading chat history

    #     chat_history.append({"role": "user", "message": user_message_text}) # Adds user's message to the history of chat

    #     formatted_chat_history = [f'{msg["role"]}: {msg["message"]}' for msg in chat_history] # Creates a list with every message

    #     prompt = "\n".join(formatted_chat_history)

    #     ai_answer = ask_gemini(prompt)
        
    #     try:
    #         if ai_answer:
    #             chat_history.append({"role": "assistant", "message": ai_answer}) # Adds Ai's answer to the history of chat

    #             message_chunks = split_message(ai_answer)
    #             for chunk in message_chunks:
    #                 bot.reply_to(message, chunk)

    #             # This code executes only for testing purposes:
    #             # formatted_chat_history = [f'{msg["role"]}: {msg["message"]}' for msg in chat_history]
    #             # prompt = "\n".join(formatted_chat_history)
    #             # print(f"AI answered successfully. Chat history: {prompt}")
    #     except Exception as e:
    #         logging.error(f"Error: {e}") 
    # else:
    #     bot.reply_to(message, "Похоже, вы ошиблись, такой команды нет. Введите /help для получения списка действующих команд.")


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
    if model:
        ai_response = generate_gemini_response(prompt)
        return ai_response
    else:
        return None


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

