import telebot
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
import database as db
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from a .env file
load_dotenv()
user_contexts = {}

def setup_bot():
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
    except Exception as e:
        logging.error(f"Error initializing the bot: {e}")
        exit(1)
    
def setup_ai():
    logging.info("Gemini model is initializing...")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Checks if the Gemini API key is set; if not, AI functionality will be unavailable. 
    if not GEMINI_API_KEY:
        logging.error("Error: The 'GEMINI_API_KEY' environment variable is not set.")
    else:
        try: 
            genai.configure(api_key=GEMINI_API_KEY)

            model = genai.GenerativeModel("gemini-2.5-pro") # You can change the model here if needed.

            logging.info("Gemini model is initialized successfully.")
            return model
        except Exception as e:
            logging.error(f"Error initializing the AI model: {e}")

bot = setup_bot()
model = setup_ai()

def generate_gemini_response(prompt: str) -> str | None:
    if not model:
        logging.error("Error: Gemini model is not initialized.")
        return None
    
    try: 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error generating response from AI model: {e}")
        return None

@bot.message_handler(commands=['start'])
def main(message):

    # Add user to our database if it doesn't exist yet
    user_id = message.from_user.id
    db.add_user_if_not_exists(user_id)

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
                          "/stop_ai_chat - остановить чат с ИИ\n", parse_mode="html")


@bot.message_handler(commands=['new_ai_chat'])
def start_ai_chat(message):
    chatid = message.chat.id

    if chatid in user_contexts:
        bot.reply_to(message, "Режим чата с ИИ уже запущен. Остановите его с помощью команды /stop_ai_chat или продолжайте общение.")
    else:
        user_contexts[chatid] = []
        bot.reply_to(message, "Вы запустили режим чата с ИИ. Теперь можете задавать вопросы ИИ.")



@bot.message_handler(commands=['stop_ai_chat'])
def stop_ai_chat(message):
    chatid = message.chat.id
    if chatid in user_contexts:
        del user_contexts[chatid]
        bot.reply_to(message, "Вы остановили режим чата с ИИ.")
    else:
        bot.reply_to(message, "У вас нет актичного чата с ИИ.")

# This function is handling every message bot receives that didn't match any previous commands.
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chatid = message.chat.id # Gets unique chat id

    user_message_text = message.text # Gets user's message

    if chatid in user_contexts: # Check if user has chat with AI right now

        chat_history = user_contexts[chatid] # Loading chat history

        chat_history.append({"role": "user", "message": user_message_text}) # Adds user's message to the history of chat

        formatted_chat_history = [f'{msg["role"]}: {msg["message"]}' for msg in chat_history] # Creates a list with every message

        prompt = "\n".join(formatted_chat_history)

        ai_answer = ask_gemini(prompt)
        
        try:
            if ai_answer:
                chat_history.append({"role": "assistant", "message": ai_answer}) # Adds Ai's answer to the history of chat

                message_chunks = split_message(ai_answer)
                for chunk in message_chunks:
                    bot.reply_to(message, chunk)

                # This code executes only for testing purposes:
                # formatted_chat_history = [f'{msg["role"]}: {msg["message"]}' for msg in chat_history]
                # prompt = "\n".join(formatted_chat_history)
                # print(f"AI answered successfully. Chat history: {prompt}")
        except Exception as e:
            logging.error(f"Error: {e}") 
    else:
        bot.reply_to(message, "Похоже, вы ошиблись, такой команды нет. Введите /help для получения списка действующих команд.")


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

