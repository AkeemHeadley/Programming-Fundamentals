# ==========================================================
# Author: Akeem Headley
# Date: June 7, 2026
# Program: Personal Fitness Tracker
# Tier Attempted: Advanced
#
# Test Results:
# 180 cal / 45 min -> 4.0 -> Low
# 300 cal / 40 min -> 7.5 -> Moderate
# 320 cal / 30 min -> 10.7 -> High
# 250 cal / 50 min -> 5.0 -> Moderate
# 200 cal / 20 min -> 10.0 -> High
# ==========================================================


# ---------------------------
# BASE FUNCTIONS
# ---------------------------

def calories_per_minute(calories, duration):
    return round(calories / duration, 1)


def get_intensity(rate):

    if rate < 5.0:
        return "Low"

    elif rate < 10.0:
        return "Moderate"

    else:
        return "High"


# ---------------------------
# INTERMEDIATE FUNCTIONS
# ---------------------------

def calculate_total(values):

    total = 0

    for value in values:
        total += value

    return total


def calculate_average(values):

    total = calculate_total(values)

    return round(total / len(values), 1)


def find_best_workout(names, calories_list):

    best_index = 0

    for i in range(len(calories_list)):

        if calories_list[i] > calories_list[best_index]:
            best_index = i

    return names[best_index]


# ---------------------------
# ADVANCED FUNCTIONS
# ---------------------------

def check_goal(total_calories, goal):

    if total_calories >= goal:
        return f"Goal reached! You burned {total_calories} calories."

    short = goal - total_calories

    return f"{short} calories short of your {goal}-calorie goal."


def format_workout_row(name, duration, calories, width=20):

    rate = calories_per_minute(calories, duration)

    intensity = get_intensity(rate)

    row = (
        f"{name:<{width}}"
        f"{duration:<10}"
        f"{calories:<10}"
        f"{rate:<10}"
        f"{intensity}"
    )

    return row


def print_workout_table(names, durations, calories_list):

    print("\n===== Workout Table =====")

    print(
        f"{'Workout':<20}"
        f"{'Duration':<10}"
        f"{'Calories':<10}"
        f"{'Rate':<10}"
        f"Intensity"
    )

    print("-" * 65)

    for i in range(len(names)):

        row = format_workout_row(
            names[i],
            durations[i],
            calories_list[i]
        )

        print(row)


def analyze_trend(calories_list):

    if len(calories_list) < 2:
        return "Not enough data"

    increases = 0
    decreases = 0

    # Nested structure: loop + conditionals
    for i in range(1, len(calories_list)):

        if calories_list[i] >= calories_list[i - 1]:
            increases += 1

        if calories_list[i] <= calories_list[i - 1]:
            decreases += 1

    if increases == len(calories_list) - 1:
        return "Improving"

    elif decreases == len(calories_list) - 1:
        return "Declining"

    else:
        return "Mixed"


# ---------------------------
# MAIN PROGRAM
# ---------------------------

print("Welcome to the Personal Fitness Tracker!")

goal = int(input("Enter your daily calorie goal: "))

workout_names = []
durations = []
calories_list = []

print("\nEnter workouts (type 'done' to finish)\n")


while True:

    workout_name = input("Workout name: ")

    if workout_name.lower() == "done":
        break

    duration = int(input("Duration (minutes): "))
    calories = int(input("Calories burned: "))

    workout_names.append(workout_name)
    durations.append(duration)
    calories_list.append(calories)

    rate = calories_per_minute(calories, duration)

    intensity = get_intensity(rate)

    print(
        f"Result: "
        f"{workout_name} | "
        f"{duration} min | "
        f"{calories} cal | "
        f"{rate} cal/min | "
        f"Intensity: {intensity}"
    )

    print()


# ---------------------------
# SUMMARY
# ---------------------------

if len(workout_names) == 0:

    print("\nNo workouts were logged.")

else:

    print_workout_table(
        workout_names,
        durations,
        calories_list
    )

    total_calories = calculate_total(calories_list)

    avg_calories = calculate_average(calories_list)

    avg_duration = calculate_average(durations)

    best_workout = find_best_workout(
        workout_names,
        calories_list
    )

    trend = analyze_trend(calories_list)

    print("\n===== Session Summary =====")

    print(f"Workouts logged : {len(workout_names)}")

    print(f"Total calories  : {total_calories}")

    print(f"Avg calories    : {avg_calories}")

    print(f"Avg duration    : {avg_duration} min")

    print(f"Best workout    : {best_workout}")

    print(f"Effort trend    : {trend}")

    print(
        "Goal check      :",
        check_goal(total_calories, goal)
    )

    print("=" * 30)


print("\nAll workouts logged. Great job staying active!")