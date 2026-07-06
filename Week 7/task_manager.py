"""
task_manager.py

Author: Akeem Headley
Date: July 5,2026
Description: Core database layer for the Personal Task & Project Manager.

"""

import csv
import sqlite3


class TaskManager:
    """Encapsulates all database operations for tasks, projects, and tags."""

    def __init__(self, db_file):
        """Opens the database file and ensures all tables exist."""
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            # Enforce foreign key constraints (off by default in SQLite).
            self.conn.execute("PRAGMA foreign_keys = ON")
            self._setup_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to database '{db_file}': {e}")
            raise

    def _setup_tables(self):
        """Private helper: creates every table (and the status index) if needed."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Pending',
                    due_date TEXT,
                    project_id INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'Active',
                    due_date TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_tags (
                    task_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (task_id, tag_id)
                )
            """)

            # Performance index on a frequently filtered column.
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)"
            )

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error setting up tables: {e}")

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------
    def add_project(self, name, description, due_date):
        """Inserts a new project row and return its new id, or None on failure."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description, due_date) VALUES (?, ?, ?)",
                (name, description, due_date),
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding project: {e}")
            return None

    def get_all_projects(self):
        """Returns every project row, ordered by name."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY name")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching projects: {e}")
            return []

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------
    def add_task(self, title, description, priority, due_date, project_id=None):
        """Inserts a new task row (optionally linked to a project) and return its id."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO tasks (title, description, priority, due_date, project_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (title, description, priority, due_date, project_id),
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding task: {e}")
            return None

    def get_all_tasks(self):
        """Returns every task row, ordered by priority then due date."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY priority, due_date")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching tasks: {e}")
            return []

    def get_tasks_by_status(self, status):
        """Returns all tasks matching a given status, ordered by priority."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY priority", (status,)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching tasks by status: {e}")
            return []

    def get_project_tasks(self, project_id):
        """Returns all tasks belonging to a specific project."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE project_id = ? ORDER BY priority, due_date",
                (project_id,),
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching project tasks: {e}")
            return []

    def get_tasks_with_project_name(self):
        """LEFT JOIN tasks with their project's name (NULL if no project)."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.priority, t.status, t.due_date, p.name
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                ORDER BY t.priority, t.due_date
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error joining tasks and projects: {e}")
            return []

    def get_project_summary(self, project_id):
        """GROUP BY query: count of tasks per status within a project."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT status, COUNT(*) FROM tasks WHERE project_id = ? GROUP BY status",
                (project_id,),
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error building project summary: {e}")
            return []

    def search_tasks(self, keyword):
        """Finds tasks whose title or description contains the given keyword."""
        try:
            cursor = self.conn.cursor()
            pattern = "%" + keyword + "%"
            cursor.execute(
                "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ?",
                (pattern, pattern),
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching tasks: {e}")
            return []

    def update_task_status(self, task_id, new_status):
        """Updates a task's status. Returns True if a row changed, False otherwise."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating task status: {e}")
            return False

    def delete_task(self, task_id):
        """Deletes a task by id. Returns True if a row was removed, False otherwise."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting task: {e}")
            return False

    def export_to_csv(self, filename):
        """Exports all tasks (with project names) to a CSV file. Returns row count."""
        rows = self.get_tasks_with_project_name()
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Priority", "Status", "Due Date", "Project"])
                count = 0
                for row in rows:
                    row = list(row)
                    if row[5] is None:
                        row[5] = "(No Project)"
                    writer.writerow(row)
                    count += 1
            return count
        except (IOError, sqlite3.Error) as e:
            print(f"Error exporting to CSV: {e}")
            return 0

    # ------------------------------------------------------------------
    # Tags (many-to-many relationship)
    # ------------------------------------------------------------------
    def add_tag(self, name):
        """Inserts a tag if it doesn't already exist, and return its id either way."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
            self.conn.commit()
            cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            print(f"Error adding tag: {e}")
            return None

    def tag_task(self, task_id, tag_id):
        """Associates a tag with a task. Returns True if a new link was created."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                (task_id, tag_id),
            )
            self.conn.commit()
            return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Error tagging task: {e}")
            return False

    def get_tasks_by_tag(self, tag_name):
        """Three-table JOIN: all tasks that carry a given tag name."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT t.*
                FROM tasks t
                JOIN task_tags tt ON t.id = tt.task_id
                JOIN tags tg ON tt.tag_id = tg.id
                WHERE tg.name = ?
                """,
                (tag_name,),
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching tasks by tag: {e}")
            return []

    def get_tags_for_task(self, task_id):
        """Returns a flat list of tag name strings attached to a given task."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT tags.name
                FROM task_tags
                JOIN tags ON task_tags.tag_id = tags.id
                WHERE task_tags.task_id = ?
                """,
                (task_id,),
            )
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error fetching tags for task: {e}")
            return []

    # ------------------------------------------------------------------
    # Transactions / bulk operations
    # ------------------------------------------------------------------
    def bulk_add_tasks(self, tasks_list):
        """Inserts many tasks in one manual transaction; rolls back on any failure."""
        try:
            self.conn.isolation_level = None
            self.conn.execute("BEGIN")
            cursor = self.conn.cursor()
            count = 0
            for t in tasks_list:
                cursor.execute(
                    """INSERT INTO tasks (title, description, priority, due_date, project_id)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        t["title"],
                        t.get("description"),
                        t.get("priority", "Medium"),
                        t.get("due_date"),
                        t.get("project_id"),
                    ),
                )
                count += 1
            self.conn.execute("COMMIT")
            return count
        except sqlite3.Error as e:
            self.conn.execute("ROLLBACK")
            print(f"Bulk insert failed, transaction rolled back: {e}")
            raise
        finally:
            self.conn.isolation_level = ""

    def import_from_csv(self, filename):
        """Reads a CSV file of tasks and bulk-insert them in a single transaction."""
        try:
            with open(filename, newline="") as f:
                reader = csv.DictReader(f)
                tasks_list = []
                for row in reader:
                    raw_pid = row.get("project_id", "")
                    project_id = int(raw_pid) if raw_pid else None
                    tasks_list.append({
                        "title": row.get("title"),
                        "description": row.get("description"),
                        "priority": row.get("priority", "Medium"),
                        "due_date": row.get("due_date"),
                        "project_id": project_id,
                    })
            return self.bulk_add_tasks(tasks_list)
        except FileNotFoundError as e:
            print(f"Import file not found: {e}")
            return 0
        except csv.Error as e:
            print(f"Error reading CSV file: {e}")
            return 0
        except sqlite3.Error as e:
            print(f"Database error during import: {e}")
            return 0

    def close(self):
        """Close the underlying database connection."""
        self.conn.close()


def display_tasks(tasks):
    """Prints a list of task tuples (id, title, description, priority, status,
    due_date, project_id) as an aligned table."""
    if not tasks:
        print("No tasks found.")
        return

    print(f"{'ID':<4}{'Title':<27}{'Priority':<11}{'Status':<13}{'Due Date':<12}")
    print(f"{'-'*3:<4}{'-'*25:<27}{'-'*9:<11}{'-'*11:<13}{'-'*10:<12}")
    for row in tasks:
        task_id, title = row[0], row[1]
        priority, status, due_date = row[3], row[4], row[5]
        short_title = title[:25]
        print(f"{task_id:<4}{short_title:<27}{priority:<11}{status:<13}{str(due_date):<12}")
