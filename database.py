'''
Handles all interactions with the SQLite database for the bot.

This module is responsible for all database operations, including initializing
the schema and providing CRUD functions for all tables.

Functions:
- initialize_db(): Creates the database and tables if they don't exist.
- add_user_if_not_exists(telegram_id): Adds a new user to the 'users' table.
- get_user_db_id(telegram_id): Retrieves the internal DB id for a user.
- add_new_chat(user_db_id, chat_name, is_active): Creates a new chat session for a user.
- get_user_chats(user_db_id): Retrieves all chats for a specific user.
- deactivate_all_user_chats(user_db_id): Sets all chats for a user to inactive.
- add_message_to_chat(chat_id, role, content): Adds a message to a specific chat.
- get_chat_history(chat_id): Retrieves the full message history for a specific chat.
- get_active_chat_id(user_db_id): Retrieves the ID of the active chat for a user. If multiple active chats are found, all are deactivated to maintain data integrity.

Database Schema:
- Table 'users':
    Stores unique bot users, identified by their telegram_id. Acts as parent for 'chats' table.

- Table 'chats':
    Stores chat sessions. Every chat must be associated with a user (via user_id).
    Acts as parent for 'messages' table.

- Table 'messages':
    Stores individual messages.
    Every message must be associated with a chat (via chat_id).
'''

import sqlite3
import os
import logging

# If DB_PATH environment variable is not set, defaults to "bot_database.db" in the current directory.
DB_PATH = os.getenv("DB_PATH", "bot_database.db")

def initialize_db():
    """
    Initializes the database.

    Creates the .db file if it doesn't exist and sets up the required table schema (users, chats, messages).

    This function is idempotent and can be safely called multiple times 
    """

    logging.info("Initializing initialize_db function...")

    try:
        # Create connection and cursor. Cursor is essential for all CRUD operations.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logging.debug(f"Connected to database at {DB_PATH}.")

        # Create the 'users' table to store unique user identifiers.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL
        );
        """)
        logging.debug("Users table ensured in database.")
        # Create the 'chats' table to store chat sessions.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        chat_name TEXT NOT NULL DEFAULT 'Новый чат',
        is_active BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """)
        logging.debug("Chats table ensured in database.")
        # Create the 'messages' table to store individual messages.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chats (id)
        );
        """)
        logging.debug("Messages table ensured in database.")

        conn.commit()

        logging.info("Database initialized and tables created if they did not exist.")
    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}", exc_info=True)
    finally:
        if conn: 
            conn.close()
            logging.debug("Database connection closed after initialization.")

def add_user_if_not_exists(telegram_id: int):
    """
    Adds new user in 'users' table if not exists.

    Args:
        telegram_id (int): Unique user identificator.
    """

    logging.info(f"Initializing user addition for telegram ID {telegram_id}...")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = "INSERT OR IGNORE INTO users (telegram_id) VALUES (?)"

        cursor.execute(sql_query, (telegram_id,))

        conn.commit()
        logging.info(f"User with telegram ID {telegram_id} added or already exists.")
    except sqlite3.Error as e:
        logging.error(f"Error adding user with telegram ID {telegram_id}: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logging.debug(f"Database connection closed after adding user with telegram ID {telegram_id}.")

def get_user_db_id(telegram_id: int) -> int | None:
    """
    Gets user inner database id by telegram id. 
    If user doesn't exist in table 'users' function will try to add him.

    Args:
        telegram_id (int): Unique user identificator.

    Returns:
        int: The internal database ID of the user or None in case of an unexpected error.
    """
    logging.info(f"Fetching DB ID for telegram ID {telegram_id}...")
    # Ensure the user exists in the database. If not, add them.
    add_user_if_not_exists(telegram_id)

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = 'SELECT id FROM users WHERE telegram_id = ?'
        cursor.execute(sql_query, (telegram_id,))
        result_tuple = cursor.fetchone()
        if result_tuple:
            result = result_tuple[0]
            logging.info(f"Fetched DB ID {result} for telegram ID {telegram_id}.")
            return result
        else:
            logging.error(f"No user found with telegram ID {telegram_id}.", exc_info=True)
            return None
    except sqlite3.Error as e:
        logging.error(f"Error fetching DB ID for telegram ID {telegram_id}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()
            logging.debug(f"Database connection closed after fetching user DB ID for telegram ID {telegram_id}.")

def add_new_chat(user_db_id: int, chat_name: str | None, is_active: bool):
    """
    Adds a new chat for a user and returns the new chat's ID.

    Args:
        user_db_id (int): The internal database ID of the user.
        chat_name (str): The chat name. Defaults to "Новый чат".
        is_active (bool): The boolean variable to indicate chat activity.
    Returns:
        int: The ID of the newly created chat or None in case of an unexpected error.
    """
    logging.info(f"Adding new chat for user {user_db_id}...")
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = "INSERT INTO chats (user_id, chat_name, is_active) VALUES (?, ?, ?)"
        cursor.execute(sql_query, (user_db_id, chat_name, is_active))

        conn.commit()

        new_chat_id = cursor.lastrowid
        logging.info(f"New chat added with ID {new_chat_id} for user {user_db_id}.")

        return new_chat_id
    except sqlite3.Error as e:
        logging.error(f"Error adding new chat for user {user_db_id}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def get_user_chats(user_db_id: int) -> list[dict] | None:
    """
    Gets list of all user's chats by inner id.

    Args:
        user_db_id (int): The internal database ID of the user.
    
    Returns:
        list[dict]: a list of dictionaries where each one represents a chat or None in case of an unexpected error.
    """
    logging.info(f"Fetching chats for user {user_db_id}...")
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = "SELECT * FROM chats WHERE user_id = ? ORDER BY created_at DESC"
        
        cursor.execute(sql_query, (user_db_id,))

        # getting a list with tuples, where each tuple represents a chat
        chats = cursor.fetchall()

        # getting a list of column's names using cursor's attribute.
        # this is needed for zipping column's names and data in each chat using dictionary, instead of tuple.

        column_names = [description[0] for description in cursor.description]

        result = [dict(zip(column_names, chat)) for chat in chats]

        logging.info(f"Fetched {len(result)} chats for user {user_db_id}.")
        return result
    except sqlite3.Error as e:
        logging.error(f"Failed to fetch chats for user_db_id {user_db_id}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()
            logging.debug(f"Database connection closed after fetching chats for user {user_db_id}.")

def deactivate_all_user_chats(user_db_id: int):
    """
    Deactivates all chats for a specific user.

    Args:
        user_db_id (int): The internal database ID of the user.
    """
    logging.info(f"Starting deactivation of all chats for user {user_db_id}...")
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = "UPDATE chats SET is_active = 0 WHERE user_id = ?"
        
        cursor.execute(sql_query, (user_db_id,))

        conn.commit()
        logging.info(f"All chats for user {user_db_id} have been deactivated.")
    except sqlite3.Error as e:
        logging.error(f"Error deactivating chats for user {user_db_id}: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logging.debug(f"Database connection closed after deactivating chats for user {user_db_id}.")

def add_message_to_chat(chat_id: int, role: str, content: str):
    """
    Adds a new message to a specific chat.

    Args:
        chat_id (int): The ID of the chat to which the message belongs.
        role (str): The role of the message sender (e.g., 'user', 'assistant').
        content (str): The content of the message.
    """
    logging.info(f"Adding new message to chat {chat_id}...")
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)"
        cursor.execute(sql_query, (chat_id, role, content))

        conn.commit()
        logging.info(f"Successfully added message to chat {chat_id}.")
    except sqlite3.Error as e:
        logging.error(f"Error adding message to chat {chat_id}. Message content: {content}. Error: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logging.debug(f"Database connection closed after adding message to chat {chat_id}.")

def get_chat_history(chat_id: int) -> list[dict] | None:
    """
    Retrieves the full message history for a specific chat.

    Args:
        chat_id (int): The ID of the chat.

    Returns:
        list[dict]: A list of dictionaries where each dictionary represents a message.
    """
    logging.info(f"Fetching message history for chat {chat_id}...")
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Fetch messages ordered by creation time to maintain conversation flow.
        sql_query = "SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC"
        
        cursor.execute(sql_query, (chat_id,))

        messages = cursor.fetchall()

        # getting a list of column's names using cursor's attribute.
        # this is needed for zipping column's names and data in each message using dictionary,
        # instead of tuple.
        column_names = [description[0] for description in cursor.description]

        # Create a list of dictionaries for each message.
        result = [dict(zip(column_names, message)) for message in messages]

        return result
    except sqlite3.Error as e:
        logging.error(f"Error fetching message history for chat {chat_id}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()
            logging.debug(f"Database connection closed after fetching message history for chat {chat_id}.")

def get_active_chat_id(user_db_id: int) -> int | None:
    """
    Retrieves the ID of the active chat for a user.
    If multiple active chats are found, all are deactivated to maintain data integrity.

    Args:
        user_db_id (int): The internal database ID of the user.
    Returns:
        int | None: The ID of the active chat, or 0 if not found.
    """
    logging.info(f"Retrieving active chat ID for user {user_db_id}...")

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # First, check how many active chats the user has.
        count_query = "SELECT COUNT(*) FROM chats WHERE user_id = ? AND is_active = 1"

        cursor.execute(count_query, (user_db_id,))
        # Fetch the count of active chats.
        active_chat_count = cursor.fetchone()[0]

        if active_chat_count > 1:
            logging.warning(f"Data integrity issue: User {user_db_id} has {active_chat_count} active chats. Deactivating all to resolve.")
            # Optionally, could deactivate all but one chat here to enforce single active chat rule.
            deactivate_all_user_chats(user_db_id)
            # In the future, logic to keep the most recent chat active should be implemented.
            logging.info(f"All chats for user {user_db_id} have been deactivated to resolve integrity issue.")
            return 0
        elif active_chat_count == 0:
            logging.info(f"Complete: No active chat found for user {user_db_id}.")
            return 0
        else: # active_chat_count == 1
            # Now, fetch the active chat ID.
            sql_query = "SELECT id FROM chats WHERE user_id = ? AND is_active = 1"
            cursor.execute(sql_query, (user_db_id,))

            active_chat = cursor.fetchone()

            if active_chat:
                logging.info(f"Completed: Found active chat ID {active_chat[0]} for user {user_db_id}.")
                return active_chat[0]
            else:
                logging.error(f"Data integrity issue: No active chat found for user {user_db_id} despite earlier check.")
                return None
    except sqlite3.Error as e:
        logging.error(f"Error retrieving active chat ID for user {user_db_id}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()
            logging.debug(f"Database connection closed after retrieving active chat ID for user {user_db_id}.")

if __name__ == '__main__':

    # Get log level from environment variable, default to INFO if not set
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Set up logging configuration
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    logging.info("Logging is set up.")

    logging.info("Database is initializing...")
    initialize_db()
    logging.info("Database initialized successfully.")