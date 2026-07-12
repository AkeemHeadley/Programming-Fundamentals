# =============================================================================
# Student Record Management System
# Week 8 Refactoring Exercise
#
# This program reads student data from a CSV file and provides a menu-driven
# interface to list all students and search for a student by ID.
# =============================================================================

import csv

# -----------------------------------------------------------------------------
# Global Variables
# -----------------------------------------------------------------------------
student_records = []        # Holds all student records loaded from the CSV
csv_filename = ""           # Stores the filename entered by the user
menu_choice = ""            # Stores the user's menu selection
csv_loaded = False          # Tracks whether a CSV file has been loaded

search_id = ""              # Stores the Student ID entered during a search
found_student = None        # Stores the matching student record, if found
search_index = 0            # Loop counter used during linear search

row_number = 0               # Loop counter used when printing student records
current_student = None      # Holds the current record during iteration

student_id = ""             # Fields parsed from each CSV row
student_name = ""
major = ""
gpa = ""
total_credits = ""

# =============================================================================
# Main Program Loop
# =============================================================================

print("=" * 60)
print("   Student Record Management System")
print("=" * 60)

while True:

    # -------------------------------------------------------------------------
    # Display Menu
    # -------------------------------------------------------------------------
    print()
    print("Please select an option:")
    print("  1. Read CSV")
    print("  2. List CSV Contents")
    print("  3. Search for Student by ID")
    print("  4. Exit")
    print()

    menu_choice = input("Enter your choice (1-4): ").strip()

    # =========================================================================
    # Option 1: Read CSV
    # =========================================================================
    if menu_choice == "1":

        csv_filename = input("Enter the CSV filename (e.g., students.csv): ").strip()

        # BUG FIX (#3): student_records must be cleared before a (re)load,
        # otherwise reloading the same file appends a second copy of every row.
        student_records = []

        csv_file = open(csv_filename, newline="")
        csv_reader = csv.DictReader(csv_file)
        # BUG FIX (#1): the file was being closed BEFORE the DictReader was
        # iterated. DictReader reads lazily from the underlying file object,
        # so closing it early caused "I/O operation on closed file" as soon
        # as the for-loop below tried to pull rows from it.

        for row in csv_reader:
            student_id     = row["StudentID"]
            student_name   = row["StudentName"]
            major          = row["Major"]
            gpa            = row["GPA"]
            total_credits  = row["TotalCredits"]

            student_record = {
                "StudentID"    : student_id,
                "StudentName"  : student_name,
                "Major"        : major,
                "GPA"          : gpa,
                "TotalCredits" : total_credits
            }

            student_records.append(student_record)

        csv_file.close()

        # BUG FIX (#4): csv_loaded was declared but never set to True, so
        # Options 2 and 3 always believed no data had been loaded.
        csv_loaded = True

        print()
        print(f"Success! {len(student_records)} student record(s) loaded from '{csv_filename}'.")

    # =========================================================================
    # Option 2: List CSV Contents
    # =========================================================================
    elif menu_choice == "2":

        if not csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")

        else:
            print()
            print("-" * 80)
            # BUG FIX (#5): the header used spaces between fields while the
            # data rows below did not, which threw the columns out of
            # alignment. Both now rely on field width alone, with no
            # in-between spaces, so the columns line up.
            print(f"{'#':<5}{'Student ID':<12}{'Student Name':<22}{'Major':<24}{'GPA':<6}{'Credits'}")
            print("-" * 80)

            row_number = 1

            for current_student in student_records:
                print(
                    f"{row_number:<5}"
                    f"{current_student['StudentID']:<12}"
                    f"{current_student['StudentName']:<22}"
                    f"{current_student['Major']:<24}"
                    f"{current_student['GPA']:<6}"
                    f"{current_student['TotalCredits']}"
                )
                row_number = row_number + 1

            print("-" * 80)
            print(f"Total records: {len(student_records)}")

    # =========================================================================
    # Option 3: Search for Student by ID
    # =========================================================================
    elif menu_choice == "3":

        if not csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")

        else:
            search_id = input("Enter the Student ID to search for: ").strip().upper()

            # BUG FIX (#9): found_student must be reset before every new
            # search. Previously a match from an earlier search could still
            # be sitting in found_student, so a *second* search for an ID
            # that does NOT exist would incorrectly re-display the old match.
            found_student = None
            search_index = 0

            # BUG FIX (#2): the loop condition used "<=" instead of "<",
            # which let search_index reach an index equal to
            # len(student_records) -- one past the last valid index -- and
            # triggered "list index out of range". The "force loop to end"
            # trick was also unreliable; a plain "<" bound combined with
            # stopping as soon as a match is found fixes both problems.
            while search_index < len(student_records) and found_student is None:
                # BUG FIX (#10): search_id is now uppercased above (case-
                # insensitive, whitespace-tolerant search), matching the
                # .upper() already applied to the stored StudentID.
                if student_records[search_index]["StudentID"].upper() == search_id:
                    found_student = student_records[search_index]
                else:
                    search_index = search_index + 1

            print()

            if found_student is None:
                print(f"No student found with ID '{search_id}'.")
            else:
                print("Student found!")
                print("-" * 40)
                # BUG FIX (#8): the dictionary key is "StudentID", not
                # "Student_ID" -- the typo caused a KeyError whenever a
                # match was found.
                print(f"  Student ID    : {found_student['StudentID']}")
                print(f"  Student Name  : {found_student['StudentName']}")
                print(f"  Major         : {found_student['Major']}")
                print(f"  GPA           : {found_student['GPA']}")
                print(f"  Total Credits : {found_student['TotalCredits']}")
                print("-" * 40)

    # =========================================================================
    # Option 4: Exit
    # =========================================================================
    # BUG FIX (#6): menu_choice is always a string (input().strip() never
    # returns an int), so "menu_choice == 4" could never be True. Comparing
    # against the string "4" lets the Exit option actually run.
    elif menu_choice == "4":
        print()
        print("Thank you for using the Student Record Management System. Goodbye!")
        break

    # =========================================================================
    # Invalid Input
    # =========================================================================
    else:
        print()
        print(f"'{menu_choice}' is not a valid option. Please enter 1, 2, 3, or 4.")
