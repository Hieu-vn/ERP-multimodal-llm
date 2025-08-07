# -*- coding: utf-8 -*-
"""
ERP Client Interface
This module provides a centralized client for interacting with the ERP system.
It now uses SQLite for the transactional database.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the database
DB_PATH = Path(__file__).parent / "data" / "erp_main.db"

class ERPClient:
    """
    A client for interacting with the ERP's transactional database (SQLite).
    """

    def _get_db_connection(self):
        """Creates and returns a new database connection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        return conn

    # --- Task Management Methods ---

    def create_task(self, title: str, description: str, assignee_id: str, reporter_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new task and saves it to the database."""
        logger.info(f"Creating task for assignee '{assignee_id}' in project '{project_id}' with title '{title}'")
        conn = self._get_db_connection()
        try:
            # Generate a unique task_id
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]
            task_id = f"T-{task_count + 1}"

            sql = ''' INSERT INTO tasks(task_id, project_id, title, description, assignee_id, reporter_id, status, created_at, updated_at)
                      VALUES(?,?,?,?,?,?,?,?,?)'''
            
            current_time = datetime.utcnow().isoformat()
            task_data = (task_id, project_id, title, description, assignee_id, reporter_id, "Mới tạo", current_time, current_time)
            
            cursor.execute(sql, task_data)
            conn.commit()
            task_id_db = cursor.lastrowid
            logger.info(f"Successfully created task with DB ID: {task_id_db} and Task ID: {task_id}")
            return {"id": task_id_db, "task_id": task_id, "title": title}
        except sqlite3.Error as e:
            logger.error(f"Database error in create_task: {e}")
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()

    def get_tasks_by_assignee(self, assignee_id: str) -> List[Dict[str, Any]]:
        """Retrieves all tasks assigned to a specific user."""
        logger.info(f"Fetching tasks for assignee '{assignee_id}'")
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE assignee_id=?", (assignee_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error in get_tasks_by_assignee: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_tasks_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Retrieves all tasks for a specific project."""
        logger.info(f"Fetching tasks for project '{project_id}'")
        conn = self._get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE project_id=?", (project_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error in get_tasks_by_project: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        """Updates the status of a specific task."""
        logger.info(f"Updating status for task '{task_id}' to '{new_status}'")
        conn = self._get_db_connection()
        try:
            sql = ''' UPDATE tasks
                      SET status = ? ,
                          updated_at = ?
                      WHERE task_id = ?'''
            current_time = datetime.utcnow().isoformat()
            cursor = conn.cursor()
            cursor.execute(sql, (new_status, current_time, task_id))
            conn.commit()
            if cursor.rowcount == 0:
                raise sqlite3.Error(f"Task with ID '{task_id}' not found for update.")
            return {"task_id": task_id, "status": "updated", "new_status": new_status}
        except sqlite3.Error as e:
            logger.error(f"Database error in update_task_status: {e}")
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()
