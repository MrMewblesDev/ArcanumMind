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

# If DB_PATH environment variable is not set, defaults to "bot_database.db" in the current directory.
DB_PATH = os.getenv("DB_PATH", "bot_database.db")

def initialize_db():
    """
    Initializes the database.

    Creates the .db file if it doesn't exist and sets up the required table schema (users, chats, messages).

    This function is idempotent and can be safely called multiple times 
    """
    # Create connection and cursor. Cursor is essential for all CRUD operations.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the 'users' table to store unique user identifiers.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL
    );
    """)

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

    # Save database and close connection.
    conn.commit()
    conn.close()

def add_user_if_not_exists(telegram_id: int):
    """
    Adds new user in 'users' table if not exists.

    Args:
        telegram_id (int): Unique user identificator.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql_query = "INSERT OR IGNORE INTO users (telegram_id) VALUES (?)"

    cursor.execute(sql_query, (telegram_id,))

    conn.commit()
    conn.close()

def get_user_db_id(telegram_id: int):
    """
    Gets user inner database id by telegram id. 
    If user doesn't exist in table 'users' function will try to add him.

    Args:
        telegram_id (int): Unique user identificator.

    Returns:
        int: The internal database ID of the user or None in case of an unexpected error.
    """

    add_user_if_not_exists(telegram_id)

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = 'SELECT id FROM users WHERE telegram_id = ?'
        cursor.execute(sql_query, (telegram_id,))
        result_tuple = cursor.fetchone()
        if result_tuple:
            return result_tuple[0]
        else:
            return None    
    finally:
        if conn:
            conn.close()

def add_new_chat(user_db_id: int, chat_name: str | None, is_active: bool):
    """
    Adds a new chat for a user and returns the new chat's ID.

    Args:
        user_db_id (int): The internal database ID of the user.
        chat_name (str): The chat name. Defaults to "Новый чат".
        is_active (bool): The boolean variable to indicate chat activity.
    Returns:
        int: The ID of the newly created chat.
    """
    
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        sql_query = "INSERT INTO chats (user_id, chat_name, is_active) VALUES (?, ?, ?)"
        cursor.execute(sql_query, (user_db_id, chat_name, is_active))

        conn.commit()

        new_chat_id = cursor.lastrowid

        return new_chat_id
    finally:
        if conn:
            conn.close()

def get_user_chats(user_db_id: int):
    """
    Gets list of all user's chats by inner id.

    Args:
        user_db_id (int): The internal database ID of the user.
    
    Returns:
        list[dict]: a list of dictionaries where each one represents a chat.
    """
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

        return [dict(zip(column_names, chat)) for chat in chats]
    finally:
        if conn:
            conn.close()

        


if __name__ == '__main__':
    initialize_db()