# =============================================================================
# Student Record Management System (Refactored, Object-Oriented Version)
# Programming Fundamentals with Python - Week 8 Refactoring Exercise
#
# Same external behaviour as student_records_fixed.py, redesigned around a
# Student class and a StudentRoster class instead of global variables and
# top-down script logic.
# =============================================================================

import csv


class Student:
    """Represents a single student record loaded from the CSV file."""

    def __init__(self, student_id, student_name, major, gpa, total_credits):
        """Store the five fields that make up one student record."""
        self.student_id = student_id
        self.student_name = student_name
        self.major = major
        self.gpa = gpa
        self.total_credits = total_credits

    def __str__(self):
        """Return a human-readable, single-line summary of the student."""
        return (
            f"{self.student_id:<12}{self.student_name:<22}"
            f"{self.major:<24}{self.gpa:<6}{self.total_credits}"
        )


class GraduateStudent(Student):
    """A Student who is also pursuing a graduate thesis (bonus feature)."""

    def __init__(self, student_id, student_name, major, gpa, total_credits, thesis_topic):
        """Store the standard student fields plus a thesis topic."""
        super().__init__(student_id, student_name, major, gpa, total_credits)
        self.thesis_topic = thesis_topic

    def __str__(self):
        """Return the standard student summary with the thesis topic appended."""
        base = super().__str__()
        return f"{base}  (Thesis: {self.thesis_topic})"


class StudentRoster:
    """Owns the collection of Student objects and every menu action."""

    def __init__(self):
        """Initialize an empty roster with no CSV file loaded yet."""
        self.students = []
        self.csv_loaded = False
        self.csv_filename = ""

    def load_csv(self, filename):
        """
        Read student records from a CSV file into self.students.

        Returns True on success, False if the file could not be read.
        Any previously loaded records are discarded first so that reloading
        the same (or a different) file never produces duplicate entries.
        """
        try:
            with open(filename, newline="") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                new_students = []

                for row in csv_reader:
                    try:
                        student = Student(
                            row["StudentID"].strip(),
                            row["StudentName"].strip(),
                            row["Major"].strip(),
                            row["GPA"].strip(),
                            row["TotalCredits"].strip(),
                        )
                    except KeyError:
                        # A row was missing one of the expected columns;
                        # skip it rather than letting the whole load fail.
                        continue
                    new_students.append(student)

            # Keep the roster sorted by StudentID so binary search works.
            new_students.sort(key=lambda s: s.student_id.upper())

            self.students = new_students
            self.csv_filename = filename
            self.csv_loaded = True
            return True

        except FileNotFoundError:
            print()
            print(f"Error: could not find a file named '{filename}'.")
            return False
        except OSError as error:
            print()
            print(f"Error: could not read '{filename}' ({error}).")
            return False

    def list_students(self):
        """Print every loaded student in a numbered, formatted table."""
        if not self.csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")
            return

        print()
        print("-" * 80)
        print(f"{'#':<5}{'Student ID':<12}{'Student Name':<22}{'Major':<24}{'GPA':<6}{'Credits'}")
        print("-" * 80)

        row_number = 1
        for student in self.students:
            print(f"{row_number:<5}{student}")
            row_number = row_number + 1

        print("-" * 80)
        print(f"Total records: {len(self.students)}")

    def search_by_id(self, search_id):
        """
        Look up a student by ID using binary search (self.students is kept
        sorted by student_id). Returns the matching Student, or None.
        """
        target = search_id.strip().upper()

        low = 0
        high = len(self.students) - 1
        found = None

        while low <= high and found is None:
            mid = (low + high) // 2
            mid_id = self.students[mid].student_id.upper()

            if mid_id == target:
                found = self.students[mid]
            elif mid_id < target:
                # Target is alphabetically after the middle element, so
                # search the right half next.
                low = mid + 1
            else:
                # Target is alphabetically before the middle element, so
                # search the left half next.
                high = mid - 1

        return found

    def handle_search(self):
        """Prompt for a Student ID, run the search, and display the result."""
        if not self.csv_loaded:
            print()
            print("No data loaded. Please use Option 1 to read a CSV file first.")
            return

        search_id = input("Enter the Student ID to search for: ").strip()
        found_student = self.search_by_id(search_id)

        print()
        if found_student is None:
            print(f"No student found with ID '{search_id.upper()}'.")
        else:
            print("Student found!")
            print("-" * 40)
            print(f"  Student ID    : {found_student.student_id}")
            print(f"  Student Name  : {found_student.student_name}")
            print(f"  Major         : {found_student.major}")
            print(f"  GPA           : {found_student.gpa}")
            print(f"  Total Credits : {found_student.total_credits}")
            print("-" * 40)

    def handle_load(self):
        """Prompt for a filename and load it, reporting success or failure."""
        filename = input("Enter the CSV filename (e.g., students.csv): ").strip()
        if self.load_csv(filename):
            print()
            print(f"Success! {len(self.students)} student record(s) loaded from '{filename}'.")

    def run(self):
        """Run the main menu loop until the user chooses to exit."""
        print("=" * 60)
        print("   Student Record Management System")
        print("=" * 60)

        while True:
            print()
            print("Please select an option:")
            print("  1. Read CSV")
            print("  2. List CSV Contents")
            print("  3. Search for Student by ID")
            print("  4. Exit")
            print()

            menu_choice = input("Enter your choice (1-4): ").strip()

            if menu_choice == "1":
                self.handle_load()
            elif menu_choice == "2":
                self.list_students()
            elif menu_choice == "3":
                self.handle_search()
            elif menu_choice == "4":
                print()
                print("Thank you for using the Student Record Management System. Goodbye!")
                break
            else:
                print()
                print(f"'{menu_choice}' is not a valid option. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    roster = StudentRoster()
    roster.run()
