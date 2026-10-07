#!/usr/bin/env python3
"""
Escape Room Database Initializer
Executes schema.sql against the local MySQL instance to create/verify all
tables, seed rooms, puzzles, clues, and initialize the leaderboard view.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error


def init_database():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "titimylove")
    database = os.getenv("DB_NAME", "escape_room")

    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")

    if not os.path.exists(schema_file):
        print(f"Error: schema file not found at {schema_file}")
        sys.exit(1)

    print(f"Connecting to MySQL at {host}:{port} as '{user}'...")

    try:
        # First connect without specifying database in case it needs to be created
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )

        cursor = connection.cursor()

        # If escape_room already exists, ensure image_path column exists and prune old rooms
        try:
            cursor.execute(f"USE `{database}`;")
            try:
                cursor.execute("ALTER TABLE `puzzles` ADD COLUMN `image_path` VARCHAR(255) DEFAULT NULL;")
            except Error:
                pass
            try:
                cursor.execute("DELETE FROM `game_sessions` WHERE `room_id` NOT IN (1, 2, 3);")
                cursor.execute("DELETE FROM `rooms` WHERE `room_id` NOT IN (1, 2, 3);")
                cursor.execute("DELETE FROM `puzzles` WHERE `room_id` NOT IN (1, 2, 3);")
                cursor.execute("DELETE FROM `clues` WHERE `puzzle_id` NOT IN (SELECT `puzzle_id` FROM `puzzles`);")
                connection.commit()
            except Error:
                pass
        except Error:
            pass

        print(f"Reading {schema_file}...")
        with open(schema_file, "r", encoding="utf-8") as f:
            sql_script = f.read()

        print("Executing schema script...")
        # Split statements by semicolon, ignoring empty lines or comments
        statements = []
        statement_buffer = []
        in_delimiter = False

        for line in sql_script.splitlines():
            stripped = line.strip()
            if stripped.startswith("--") or not stripped:
                continue
            statement_buffer.append(line)
            if stripped.endswith(";"):
                statements.append("\n".join(statement_buffer))
                statement_buffer = []

        success_count = 0
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                    success_count += 1
                except Error as err:
                    # Ignore duplicate warnings or continue
                    print(f"Notice executing statement: {err}")

        connection.commit()
        print(f"Successfully processed {success_count} SQL statements.")

        # Reconnect to escape_room database to query verification stats
        cursor.execute(f"USE `{database}`;")

        cursor.execute("SELECT COUNT(*) FROM rooms;")
        room_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM puzzles;")
        puzzle_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clues;")
        clue_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM teams;")
        team_count = cursor.fetchone()[0]

        print("\nDatabase verification summary:")
        print(f"  • Escape Rooms: {room_count}")
        print(f"  • Puzzles:      {puzzle_count}")
        print(f"  • Clues/Hints:  {clue_count}")
        print(f"  • Teams:        {team_count}")
        print("\nDatabase initialization complete and verified!")

        cursor.close()
        connection.close()

    except Error as e:
        print(f"Database error during initialization: {e}")
        print("Please check MySQL connection details and ensure the MySQL server is running.")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
