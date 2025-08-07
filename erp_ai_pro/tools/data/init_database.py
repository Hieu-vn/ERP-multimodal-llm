# -*- coding: utf-8 -*-
"""
One-time script to initialize the SQLite database and create tables.
"""

import sqlite3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the database file
DB_PATH = Path(__file__).parent / "erp_main.db"

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.info(f"Successfully connected to SQLite database at {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to SQLite database: {e}")
        return None

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        logger.info("Table created successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error creating table: {e}")

def main():
    """Main function to initialize the database and tables."""
    sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS tasks (
                                        id integer PRIMARY KEY,
                                        task_id text NOT NULL UNIQUE,
                                        project_id text,
                                        title text NOT NULL,
                                        description text,
                                        assignee_id text NOT NULL,
                                        reporter_id text NOT NULL,
                                        status text NOT NULL,
                                        created_at text NOT NULL,
                                        updated_at text NOT NULL
                                    ); """

    conn = create_connection()

    if conn is not None:
        # Create tasks table
        create_table(conn, sql_create_tasks_table)
        conn.close()
    else:
        logger.error("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
