"""
Personal Expense Tracker
Author: Akeem Headley
Date: June 14, 2026
Tier: Advanced

"""

import os
import csv
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ----------------------------
# FUNCTION 1: BUILD RECORD
# ----------------------------
def build_record(description, amount, category):
    today = str(datetime.date.today())

    description = description[:30]
    formatted_amount = f"{float(amount):.2f}"

    return ",".join([today, description, formatted_amount, category])


# ----------------------------
# FUNCTION 2: LOAD RECORDS
# ----------------------------
def load_records(filename):
    records = []

    full_path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(full_path):
        return records

    try:
        with open(full_path, "r", newline="") as file:
            reader = csv.reader(file)

            for row in reader:
                if not row:
                    continue

                if row[0].lower() == "date":
                    continue

                records.append(row)

    except Exception as e:
        print(f"Error loading file: {e}")

    return records


# ----------------------------
# FUNCTION 3: DISPLAY RECORDS 
# ----------------------------
def display_records(records):
    if not records:
        print("\nNo expenses on record yet.\n")
        return

    print("\nDate        Description                   Amount     Category")
    print("-" * 70)

    for r in records:
        try:
            print(f"{r[0]:<12}{r[1]:<30}${float(r[2]):<10.2f}{r[3]:<15}")
        except ValueError:
            continue


# ----------------------------
# VALIDATION FUNCTIONS
# ----------------------------
def get_valid_amount():
    while True:
        try:
            return float(input("Enter amount: "))
        except ValueError:
            print("Invalid amount. Please enter a number.")


def get_valid_category():
    while True:
        category = input("Enter category: ").strip()
        if category and category[0].isalpha():
            return category
        print("Invalid category. Must start with a letter.")


# ----------------------------
# FUNCTION 4: SEARCH
# ----------------------------
def search_expenses(records, keyword):
    keyword = keyword.lower()
    return [
        r for r in records
        if keyword in r[1].lower() or keyword in r[3].lower()
    ]


# ----------------------------
# FUNCTION 5: TOTALS
# ----------------------------
def calculate_totals(records):
    totals = []

    for r in records:
        category = r[3]
        amount = float(r[2])

        found = False
        for i in range(len(totals)):
            if totals[i][0] == category:
                totals[i] = (category, totals[i][1] + amount)
                found = True
                break

        if not found:
            totals.append((category, amount))

    totals.sort(key=lambda x: x[1], reverse=True)
    return totals


# ----------------------------
# FUNCTION 6: FILTER BY MONTH
# ----------------------------
def filter_by_month(records, year, month):
    return [
        r for r in records
        if r[0][:4] == year and r[0][5:7] == month
    ]


# ----------------------------
# FUNCTION 7: SAVE RECORD 
# ----------------------------
def save_record(filename, record):
    full_path = os.path.join(BASE_DIR, filename)
    file_exists = os.path.exists(full_path)

    with open(full_path, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Date", "Description", "Amount", "Category"])

        writer.writerow(record.split(","))


# ----------------------------
# FUNCTION 8: REPORT
# ----------------------------
def generate_report(records, filename):
    full_path = os.path.join(BASE_DIR, filename)

    totals = calculate_totals(records)

    today = datetime.date.today()
    year = str(today.year)
    month = f"{today.month:02d}"

    this_month = filter_by_month(records, year, month)

    total_spent = sum(float(r[2]) for r in records)
    month_spent = sum(float(r[2]) for r in this_month)

    lines = [
        "EXPENSE SUMMARY REPORT",
        f"Generated: {today}",
        "",
        f"Total records: {len(records)}",
        f"Total spending: ${total_spent:.2f}",
        "",
        "Spending by Category:"
    ]

    for cat, amt in totals:
        lines.append(f"{cat:<15} ${amt:.2f}")

    lines.extend([
        "",
        f"This Month ({year}-{month})",
        f"Records: {len(this_month)}",
        f"Spent: ${month_spent:.2f}"
    ])

    with open(full_path, "w") as f:
        for line in lines:
            f.write(line + "\n")

    return len(lines)


# ----------------------------
# MAIN PROGRAM
# ----------------------------
def main():
    filename = "expenses.csv"
    report_file = "expense_report.txt"

    try:
        records = load_records(filename)
        display_records(records)

        num = int(input("\nHow many expenses do you want to add? "))

    except ValueError:
        print("Invalid number for expense count.")
        return

    for i in range(num):
        print(f"\n--- Expense {i+1} ---")

        desc = input("Enter description: ")
        amount = get_valid_amount()
        category = get_valid_category()

        record_str = build_record(desc, amount, category)
        save_record(filename, record_str)

    records = load_records(filename)

    print("\n===== Updated Records =====")
    display_records(records)

    choice = input("\nSearch expenses? (yes/no): ").lower()
    if choice == "yes":
        keyword = input("Enter keyword: ")
        results = search_expenses(records, keyword)

        if results:
            display_records(results)
        else:
            print("No matches found.")

    print("\n===== Spending by Category =====")
    for cat, amt in calculate_totals(records):
        print(f"{cat:<15} ${amt:.2f}")

    lines = generate_report(records, report_file)
    print(f"\nReport saved ({lines} lines).")

    print("\nThank you for using Expense Tracker. Goodbye!")


if __name__ == "__main__":
    main()
