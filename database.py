import os
import mysql.connector
from mysql.connector import Error


def create_connection():
    """
    Establishes and returns a connection to the Escape Room MySQL database.
    Reads connection parameters from environment variables with safe defaults.
    """
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "titimylove")
    database = os.getenv("DB_NAME", "escape_room")

    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            return connection

    except Error as error:
        # Fallback to localhost if 127.0.0.1 had an issue
        if host == "127.0.0.1":
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    port=port,
                    user=user,
                    password=password,
                    database=database
                )
                if connection.is_connected():
                    return connection
            except Error:
                pass

        print(f"Database connection failed: {error}")
        print("Troubleshooting tips:")
        print("1. Ensure MySQL service is running (e.g. in macOS System Settings -> MySQL or 'sudo mysql.server start').")
        print("2. Verify credentials in database.py or set DB_PASSWORD environment variable.")
        print("3. Ensure database 'escape_room' exists (run: python3 init_db.py).")
        return None