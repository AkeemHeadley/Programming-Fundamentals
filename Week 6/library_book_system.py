"""
Program: Library Book Management System
Author: Akeem Headley
Date: July 10,2026
Description: An object-oriented library catalog system that models Book
    objects (and specialized EBook, AudioBook, and ReferenceBook
    subclasses), and manages a full collection through a Library class
    that supports searching, reporting, and CSV save/load.
Tier Attempted: Advanced 
"""

import csv
import os

# The catalogs file always lives next to this script, regardless of the
# directory the program is run from.
LIBRARY_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.csv")


# ---------------------------------------------------------------------------
# BASE LEVEL: Book class
# ---------------------------------------------------------------------------
class Book:
    """Represents a single physical library book."""

    def __init__(self, title, author, isbn, year, genre):
        # Stores the core identifying data for this book.
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.genre = genre
        # Every new book starts out available with no borrower.
        self.available = True
        self.borrower = None

    def __str__(self):
        # Builds a readable, column-aligned summary line for this book.
        return (f"{self.isbn:<15} {self.title:<25} by {self.author:<20} "
                f"{self.year:<6} {self.genre:<15} {self.get_status()}")

    def check_out(self, patron_name):
        # Attempts to check the book out; caller decides what to print.
        if self.available:
            self.available = False
            self.borrower = patron_name
            return True
        return False

    def return_book(self):
        # Resets the book to available and clear the borrower.
        self.available = True
        self.borrower = None
        return f"'{self.title}' has been returned and is now available."

    def get_status(self):
        # Reports whether the book is available or who has it.
        if self.available:
            return "Available"
        return f"Checked out to {self.borrower}"


# ---------------------------------------------------------------------------
# INTERMEDIATE LEVEL: subclasses demonstrating inheritance/polymorphism
# ---------------------------------------------------------------------------
class EBook(Book):
    """A digital book that can be accessed by multiple patrons at once."""

    def __init__(self, title, author, isbn, year, genre, file_format, file_size_mb):
        super().__init__(title, author, isbn, year, genre)
        self.file_format = file_format
        self.file_size_mb = file_size_mb
        self.active_downloads = 0

    def check_out(self, patron_name):
        # Digital copies are never "unavailable" - just track downloads.
        self.active_downloads += 1
        return True

    def get_status(self):
        # Reports the current download count instead of available/checked out.
        if self.active_downloads == 0:
            return "Digital — available for download"
        return f"Digital — {self.active_downloads} active download(s)"

    def __str__(self):
        base = super().__str__()
        return base + f"\n    [Format: {self.file_format} | {self.file_size_mb} MB]"

    def get_download_info(self):
        # New method unique to EBook.
        return (f"Format: {self.file_format} | Size: {self.file_size_mb} MB | "
                f"Downloads: {self.active_downloads}")


class AudioBook(Book):
    """A narrated audio version of a book. Checks out like a normal Book."""

    def __init__(self, title, author, isbn, year, genre, narrator, duration_hours):
        super().__init__(title, author, isbn, year, genre)
        self.narrator = narrator
        self.duration_hours = duration_hours

    def __str__(self):
        base = super().__str__()
        return base + f"\n    [Narrator: {self.narrator} | Duration: {self.duration_hours} hrs]"

    def get_listening_info(self):
        # New method unique to AudioBook.
        info = f"Narrated by {self.narrator}. Listening time: {self.duration_hours} hours."
        if self.duration_hours > 10:
            info += " (Long listen — plan accordingly!)"
        return info


class ReferenceBook(Book):
    """An in-library-only book (encyclopedia, atlas, style guide, etc.)."""

    def __init__(self, title, author, isbn, year, genre, edition):
        super().__init__(title, author, isbn, year, genre)
        self.edition = edition
        self.available = False  # permanently non-circulating

    def check_out(self, patron_name):
        # Hard constraint - printing here is intentional per assignment spec.
        print("Reference books are for in-library use only and cannot be checked out.")
        return False

    def return_book(self):
        return "Reference books do not need to be returned."

    def get_status(self):
        return f"In-Library Use Only (Edition {self.edition})"

    def __str__(self):
        base = super().__str__()
        return base + f"\n    [Reference — Edition {self.edition} — In-Library Use Only]"


# ---------------------------------------------------------------------------
# ADVANCED LEVEL: Library manager class
# ---------------------------------------------------------------------------
class Library:
    """Manages a collection of Book (and subclass) objects."""

    def __init__(self, name):
        self.name = name
        self.collection = []

    def add_book(self, book):
        self.collection.append(book)

    def remove_book(self, isbn):
        for book in self.collection:
            if book.isbn == isbn:
                self.collection.remove(book)
                return True
        return False

    def find_by_isbn(self, isbn):
        for book in self.collection:
            if book.isbn == isbn:
                return book
        return None

    def find_by_author(self, author):
        return [b for b in self.collection if author.lower() in b.author.lower()]

    def find_by_genre(self, genre):
        return [b for b in self.collection if b.genre.lower() == genre.lower()]

    def get_available_books(self):
        return [b for b in self.collection if b.available]

    def get_checked_out_books(self):
        return [b for b in self.collection if not b.available]

    def generate_report(self):
        # Build (do not print) a multi-line report string.
        total = len(self.collection)
        available = len(self.get_available_books())
        checked_out = len(self.get_checked_out_books())

        book_count = sum(1 for b in self.collection if type(b) is Book)
        ebook_count = sum(1 for b in self.collection if isinstance(b, EBook))
        audio_count = sum(1 for b in self.collection if isinstance(b, AudioBook))
        ref_count = sum(1 for b in self.collection if isinstance(b, ReferenceBook))

        lines = []
        lines.append("=" * 40)
        lines.append(f" LIBRARY REPORT: {self.name}")
        lines.append("=" * 40)
        lines.append(f"Total books in collection : {total}")
        lines.append(f"Available                 : {available}")
        lines.append(f"Checked out                : {checked_out}")
        lines.append("--- Collection by Type ---")
        lines.append(f"Print Books : {book_count}")
        lines.append(f"eBooks      : {ebook_count}")
        lines.append(f"Audiobooks  : {audio_count}")
        lines.append(f"Reference   : {ref_count}")
        lines.append("--- Currently Checked Out ---")
        checked_out_books = self.get_checked_out_books()
        if checked_out_books:
            for b in checked_out_books:
                lines.append(f"  '{b.title}' -> {b.borrower}")
        else:
            lines.append("  (none)")
        lines.append("=" * 40)
        return "\n".join(lines)

    def save_to_csv(self, filename):
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["type", "title", "author", "isbn", "year", "genre",
                                  "available", "borrower", "extra1", "extra2"])
                count = 0
                for b in self.collection:
                    if isinstance(b, EBook):
                        type_name = "EBook"
                        extra1, extra2 = b.file_format, b.file_size_mb
                    elif isinstance(b, AudioBook):
                        type_name = "AudioBook"
                        extra1, extra2 = b.narrator, b.duration_hours
                    elif isinstance(b, ReferenceBook):
                        type_name = "ReferenceBook"
                        extra1, extra2 = b.edition, ""
                    else:
                        type_name = "Book"
                        extra1, extra2 = "", ""

                    writer.writerow([type_name, b.title, b.author, b.isbn, b.year,
                                      b.genre, b.available, b.borrower or "",
                                      extra1, extra2])
                    count += 1
                return count
        except Exception as e:
            print(f"Could not save library to '{filename}': {e}")
            return 0

    def load_from_csv(self, filename):
        try:
            with open(filename, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.collection = []  # clears before loading to avoid duplicates
                count = 0
                for row in reader:
                    type_name = row["type"]
                    title, author, isbn = row["title"], row["author"], row["isbn"]
                    year, genre = int(row["year"]), row["genre"]
                    extra1, extra2 = row["extra1"], row["extra2"]

                    if type_name == "EBook":
                        book = EBook(title, author, isbn, year, genre, extra1, float(extra2))
                    elif type_name == "AudioBook":
                        book = AudioBook(title, author, isbn, year, genre, extra1, float(extra2))
                    elif type_name == "ReferenceBook":
                        book = ReferenceBook(title, author, isbn, year, genre, int(extra1))
                    else:
                        book = Book(title, author, isbn, year, genre)

                    book.available = (row["available"] == "True")
                    book.borrower = row["borrower"] if row["borrower"] else None

                    self.collection.append(book)
                    count += 1
                return count
        except FileNotFoundError:
            print(f"No existing catalog found at '{filename}'. Starting with an empty library.")
            return 0
        except ValueError as e:
            print(f"Catalog file '{filename}' contains bad data and could not be fully loaded: {e}")
            return 0
        except Exception as e:
            print(f"Unexpected error loading '{filename}': {e}")
            return 0


# ---------------------------------------------------------------------------
# BASE LEVEL main-program 
# ---------------------------------------------------------------------------
def run_base_demo():
    collection = [
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"),
        Book("Educated", "Tara Westover", "978-0399590504", 2018, "Memoir"),
        Book("Dune", "Frank Herbert", "978-0441013593", 1965, "Science Fiction"),
        Book("The Hobbit", "J.R.R. Tolkien", "978-0345339683", 1937, "Fantasy"),
        Book("Sapiens", "Yuval Noah Harari", "978-0062316097", 2011, "Nonfiction"),
        Book("1984", "George Orwell", "978-0451524935", 1949, "Dystopian"),
    ]

    print("=== Full Collection ===")
    for book in collection:
        print(book)

    print()
    result1 = collection[0].check_out("Jordan")
    if result1:
        print(f"'{collection[0].title}' checked out to Jordan.")
    else:
        print(f"'{collection[0].title}' is already checked out.")

    result2 = collection[1].check_out("Priya")
    if result2:
        print(f"'{collection[1].title}' checked out to Priya.")
    else:
        print(f"'{collection[1].title}' is already checked out.")

    result3 = collection[0].check_out("Sam")
    if not result3:
        print(f"'{collection[0].title}' is already checked out.")

    print(collection[1].return_book())

    print("\n=== Sorted by Title ===")
    for book in sorted(collection, key=lambda b: b.title):
        print(book)

    print("\n=== Available Books ===")
    available_books = [b for b in collection if b.available]
    for book in available_books:
        print(book)

    return collection


# ---------------------------------------------------------------------------
# INTERMEDIATE LEVEL main-program  (polymorphism)
# ---------------------------------------------------------------------------
def run_intermediate_demo():
    mixed_collection = [
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"),
        Book("1984", "George Orwell", "978-0451524935", 1949, "Dystopian"),
        EBook("Clean Code", "Robert C. Martin", "978-1234567890", 2008, "Programming", "EPUB", 1.2),
        EBook("Fluent Python", "Luciano Ramalho", "978-1491946008", 2015, "Programming", "PDF", 8.4),
        AudioBook("Educated", "Tara Westover", "978-0399590504", 2018, "Memoir", "Julia Whelan", 12.0),
        AudioBook("Dune", "Frank Herbert", "978-0441013593", 1965, "Science Fiction", "Simon Vance", 21.0),
        ReferenceBook("Chicago Manual of Style", "University of Chicago Press", "978-0000000001", 2017, "Reference", 17),
        ReferenceBook("Merriam-Webster's Dictionary", "Merriam-Webster", "978-0000000002", 2020, "Reference", 11),
    ]

    print("\n--- Polymorphism Demonstration ---")
    for item in mixed_collection:
        print(item)
        result = item.check_out("Test Patron")
        print(f"  check_out result: {result}")
        print(f"  status: {item.get_status()}")

    return mixed_collection


# ---------------------------------------------------------------------------
# ADVANCED LEVEL: interactive menu
# ---------------------------------------------------------------------------
def prompt_new_book():
    """Asks the user for book type and fields, and return a new Book/subclass."""
    book_type = input("Type (Book/EBook/AudioBook/ReferenceBook): ").strip()
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    isbn = input("ISBN: ").strip()
    try:
        year = int(input("Year: ").strip())
    except ValueError:
        print("Invalid year, defaulting to 2000.")
        year = 2000
    genre = input("Genre: ").strip()

    if book_type == "EBook":
        file_format = input("File format (e.g., EPUB, PDF): ").strip()
        try:
            file_size_mb = float(input("File size (MB): ").strip())
        except ValueError:
            file_size_mb = 0.0
        return EBook(title, author, isbn, year, genre, file_format, file_size_mb)
    elif book_type == "AudioBook":
        narrator = input("Narrator: ").strip()
        try:
            duration_hours = float(input("Duration (hours): ").strip())
        except ValueError:
            duration_hours = 0.0
        return AudioBook(title, author, isbn, year, genre, narrator, duration_hours)
    elif book_type == "ReferenceBook":
        try:
            edition = int(input("Edition: ").strip())
        except ValueError:
            edition = 1
        return ReferenceBook(title, author, isbn, year, genre, edition)
    else:
        return Book(title, author, isbn, year, genre)


def run_advanced_menu(library):
    menu = (
        "\n[1] Display all books   [2] Add a book\n"
        "[3] Check out a book    [4] Return a book\n"
        "[5] Search by author    [6] Search by genre\n"
        "[7] Display available books   [8] Generate report\n"
        "[q] Save and quit"
    )

    while True:
        print(menu)
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            for book in library.collection:
                print(book)
        elif choice == "2":
            library.add_book(prompt_new_book())
            print("Book added.")
        elif choice == "3":
            isbn = input("ISBN of book to check out: ").strip()
            book = library.find_by_isbn(isbn)
            if book is None:
                print("No book found with that ISBN.")
            else:
                patron = input("Patron name: ").strip()
                if book.check_out(patron):
                    print(f"'{book.title}' checked out to {patron}.")
                else:
                    print(f"'{book.title}' could not be checked out.")
        elif choice == "4":
            isbn = input("ISBN of book to return: ").strip()
            book = library.find_by_isbn(isbn)
            if book is None:
                print("No book found with that ISBN.")
            else:
                print(book.return_book())
        elif choice == "5":
            author = input("Author name (or part of it): ").strip()
            for book in library.find_by_author(author):
                print(book)
        elif choice == "6":
            genre = input("Genre: ").strip()
            for book in library.find_by_genre(genre):
                print(book)
        elif choice == "7":
            for book in library.get_available_books():
                print(book)
        elif choice == "8":
            print(library.generate_report())
        elif choice in ("q", "quit"):
            count = library.save_to_csv(LIBRARY_CSV_PATH)
            print(f"Saved {count} record(s) to {LIBRARY_CSV_PATH}. Goodbye!")
            break
        else:
            print("Invalid option, please try again.")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_base_demo()
    run_intermediate_demo()

    library = Library("Riverside Public")
    loaded = library.load_from_csv(LIBRARY_CSV_PATH)
    if loaded == 0:
        # Seed the library with starter data on first run.
        library.add_book(Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", 1925, "Classic Fiction"))
        library.add_book(Book("1984", "George Orwell", "978-0451524935", 1949, "Dystopian"))
        library.add_book(EBook("Clean Code", "Robert C. Martin", "978-1234567890", 2008, "Programming", "EPUB", 1.2))
        library.add_book(AudioBook("Dune", "Frank Herbert", "978-0441013593", 1965, "Science Fiction", "Simon Vance", 21.0))
        library.add_book(ReferenceBook("Chicago Manual of Style", "University of Chicago Press", "978-0000000001", 2017, "Reference", 17))

    run_advanced_menu(library)
