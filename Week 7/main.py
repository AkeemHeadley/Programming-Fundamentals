"""
main.py
Author: Akeem Headley
Date: July 5, 2026
Tier Attempted: ADVANCED
"""

from task_manager import TaskManager, display_tasks
from report import DatabaseReport


def main():
    # 1. Connect and set up all tables.
    try:
        tm = TaskManager("tasks.db")
    except Exception as e:
        print(f"Could not start Task Manager: {e}")
        return

    # 2. Add projects.
    proj1_id = tm.add_project(
        "Research Paper", "Final paper for Programming Fundamentals", "2025-12-15"
    )
    proj2_id = tm.add_project(
        "Job Search", "Applications and interview prep", "2026-01-31"
    )
    print(f"Project added with ID: {proj1_id}")
    print(f"Project added with ID: {proj2_id}")

    # 3. Add tasks -- mix of priorities, statuses, projects, and one with no project.
    ids = []
    ids.append(tm.add_task("Write project proposal", "Draft outline and thesis",
                            "High", "2025-11-20", proj1_id))
    ids.append(tm.add_task("Find three sources", "Peer-reviewed articles only",
                            "Medium", "2025-11-25", proj1_id))
    ids.append(tm.add_task("Fix login bug", "Session token expires too early",
                            "High", "2025-11-15", None))
    ids.append(tm.add_task("Update resume", "Add recent internship",
                            "Low", "2025-10-01", proj2_id))
    ids.append(tm.add_task("Send follow-up email", "Reply to recruiter",
                            "Medium", "2025-10-18", proj2_id))
    ids.append(tm.add_task("Read chapter 4", "Database normalization",
                            "Low", "2025-11-18", None))
    for task_id in ids:
        print(f"Task added with ID: {task_id}")

    # 4/13. Display all tasks with project names.
    print("\n=== All Tasks with Project ===")
    joined = tm.get_tasks_with_project_name()
    for row in joined:
        task_id, title, priority, status, due_date, project_name = row
        project_name = project_name or "(No Project)"
        print(f"{task_id:<4}{title[:25]:<27}{priority:<9}{status:<11}{due_date:<12}{project_name}")

    # 5. Pending tasks only.
    print("\n=== Pending Tasks ===")
    display_tasks(tm.get_tasks_by_status("Pending"))

    # 6. Updates one task's status.
    updated = tm.update_task_status(ids[2], "In Progress")
    print(f"\nStatus updated for task {ids[2]}: {updated}")

    # 7. Deletes one task.
    deleted = tm.delete_task(ids[5])
    print(f"Task {ids[5]} deleted: {deleted}")

    # 8. Displays all tasks again to show updated state.
    print("\n=== All Tasks (Updated) ===")
    display_tasks(tm.get_all_tasks())

    # 14. Projects summary (GROUP BY status within a project).
    print(f"\n=== Project Summary (Project {proj1_id}) ===")
    for status, count in tm.get_project_summary(proj1_id):
        print(f"{status}: {count}")

    # 15. Keyword search.
    print("\n=== Search: 'resume' ===")
    display_tasks(tm.search_tasks("resume"))

    # 16. Exports to CSV.
    rows_written = tm.export_to_csv("tasks_export.csv")
    print(f"\nExported {rows_written} rows to tasks_export.csv")

    # 18. Tags.
    tag_urgent = tm.add_tag("urgent")
    tag_work = tm.add_tag("work")
    tag_personal = tm.add_tag("personal")
    print(f"\nTag 'urgent' id: {tag_urgent}")
    print(f"Tag 'work' id: {tag_work}")
    print(f"Tag 'personal' id: {tag_personal}")

    tm.tag_task(ids[2], tag_urgent)
    tm.tag_task(ids[2], tag_work)
    tm.tag_task(ids[3], tag_personal)

    # 19. Tasks by tag.
    print("\n=== Tasks tagged 'work' ===")
    display_tasks(tm.get_tasks_by_tag("work"))

    # 20. Tags for a single task.
    print(f"\nTags for task {ids[2]}: {tm.get_tags_for_task(ids[2])}")

    # 21. Bulk add via manual transaction.
    bulk_tasks = [
        {"title": "Book flight", "description": "For winter break", "priority": "Medium",
         "due_date": "2025-12-10", "project_id": None},
        {"title": "Buy textbook", "description": "Used copy if possible", "priority": "Low",
         "due_date": "2025-11-30", "project_id": proj1_id},
        {"title": "Backup laptop", "description": "External drive", "priority": "High",
         "due_date": "2025-11-22", "project_id": None},
    ]
    inserted = tm.bulk_add_tasks(bulk_tasks)
    print(f"\nBulk insert complete: {inserted} tasks added")

    # 22. Full aggregate report.
    report = DatabaseReport(tm)
    print("\n" + report.generate_full_report())

    # 24. Imports from CSV if present.
    import os

    # Get directory where main.py is located
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    import_file = os.path.join(BASE_DIR, "import_tasks.csv")

    if os.path.exists(import_file):
        imported = tm.import_from_csv(import_file)
        print(f"\nImported {imported} tasks from import_tasks.csv")
    else:
        print("\nNo import_tasks.csv file found -- skipping import.")

    # 25. Close the connection.
    tm.close()


if __name__ == "__main__":
    main()
