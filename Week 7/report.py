"""
report.py

Author: Akeem Headley
Date: July 5, 2026
Description: DatabaseReport class -- builds formatted statistical report
strings (status summary, priority summary, overdue tasks) from an existing
TaskManager's connection. Part of the Advanced tier submission.
Tier Attempted: ADVANCED
"""

import sqlite3
from datetime import datetime


class DatabaseReport:
    """Generatess formatted report strings from a TaskManager's database.
    This class does not open its own connection -- it reuses the one
    already owned by the TaskManager instance passed to it.
    """

    def __init__(self, task_manager):
        self.tm = task_manager

    def get_status_summary(self):
        """Returns a formatted string counting tasks per status."""
        try:
            cursor = self.tm.conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            return f"Error building status summary: {e}"

        if not rows:
            return "No tasks in database."

        lines = ["--- Status Summary ---"]
        for status, count in rows:
            lines.append(f"{status:<15}: {count} task(s)")
        return "\n".join(lines)

    def get_priority_summary(self):
        """Returns a formatted string counting tasks per priority (High -> Low)."""
        try:
            cursor = self.tm.conn.cursor()
            cursor.execute("""
                SELECT priority, COUNT(*) FROM tasks GROUP BY priority
                ORDER BY CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                END
            """)
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            return f"Error building priority summary: {e}"

        if not rows:
            return "No tasks in database."

        lines = ["--- Priority Summary ---"]
        for priority, count in rows:
            lines.append(f"{priority:<15}: {count} task(s)")
        return "\n".join(lines)

    def get_overdue_tasks(self):
        """Returns all tasks whose due date has passed and are not Done."""
        try:
            cursor = self.tm.conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE due_date < date('now') AND status != 'Done'"
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching overdue tasks: {e}")
            return []

    def generate_full_report(self):
        """Combines status summary, priority summary, and overdue tasks into
        one multi-line report string."""
        today = datetime.now().strftime("%Y-%m-%d")
        separator = "=" * 40

        lines = [
            separator,
            " TASK MANAGER REPORT",
            f" Generated: {today}",
            separator,
            self.get_status_summary(),
            "",
            self.get_priority_summary(),
            "",
            "--- Overdue Tasks ---",
        ]

        overdue = self.get_overdue_tasks()
        if not overdue:
            lines.append("No overdue tasks.")
        else:
            lines.append(f"{'ID':<4}{'Title':<25}{'Priority':<9}{'Due Date':<11}")
            lines.append(f"{'-'*2:<4}{'-'*23:<25}{'-'*8:<9}{'-'*9:<11}")
            for row in overdue:
                task_id, title = row[0], row[1]
                priority, due_date = row[3], row[5]
                lines.append(f"{task_id:<4}{title[:23]:<25}{priority:<9}{str(due_date):<11}")

        lines.append(separator)
        return "\n".join(lines)
