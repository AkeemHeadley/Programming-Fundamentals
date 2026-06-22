"""
Author: Akeem Headley
Date: 21 June, 2026
Program: Movie Collection Manager
Tier Attempted: Advanced
"""

import csv
import os

def get_starter_movies():
    return [
        {
            "title": "Inception",
            "year": 2010,
            "genres": ["Sci-Fi", "Thriller"],
            "rating": 8.8
        },
        {
            "title": "The Shawshank Redemption",
            "year": 1994,
            "genres": ["Drama"],
            "rating": 9.3
        },
        {
            "title": "The Godfather",
            "year": 1972,
            "genres": ["Crime", "Drama"],
            "rating": 9.2
        },
        {
            "title": "Interstellar",
            "year": 2014,
            "genres": ["Sci-Fi", "Adventure"],
            "rating": 8.7
        },
        {
            "title": "Se7en",
            "year": 1995,
            "genres": ["Crime", "Thriller"],
            "rating": 8.6
        }
    ]


# -------------------------------
# BASE FUNCTIONS
# -------------------------------

def create_movie(title, year, genres, rating):
    return {
        "title": title,
        "year": year,
        "genres": genres,
        "rating": rating
    }


def display_movies(movies, heading):
    print(f"\n{heading}")
    print("-" * 80)

    if not movies:
        print("No movies in this collection.")
        return

    print(f"{'Title':30}{'Year':8}{'Genres':30}{'Rating'}")

    for movie in movies:
        genre_text = " / ".join(movie["genres"])
        print(
            f"{movie['title']:30}"
            f"{movie['year']:<8}"
            f"{genre_text:30}"
            f"{movie['rating']:.1f}"
        )


def find_top_rated(movies, n):
    return sorted(
        movies,
        key=lambda m: m["rating"],
        reverse=True
    )[:n]


def get_average_rating(movies):
    if not movies:
        return 0.0

    total = 0

    for movie in movies:
        total += movie["rating"]

    return round(total / len(movies), 2)


# -------------------------------
# INTERMEDIATE FUNCTIONS
# -------------------------------

def filter_by_genre(movies, genre):
    results = []

    for movie in movies:
        for g in movie["genres"]:
            if g.lower() == genre.lower():
                results.append(movie)
                break

    return results


def update_rating(movies, title, new_rating):
    for movie in movies:
        if movie["title"].lower() == title.lower():
            movie["rating"] = new_rating
            return True
    return False


def get_genre_stats(movies):
    unique = []

    for movie in movies:
        for g in movie["genres"]:
            if g not in unique:
                unique.append(g)

    stats = []

    for genre in unique:
        total = 0
        count = 0

        for movie in movies:
            if genre in movie["genres"]:
                total += movie["rating"]
                count += 1

        stats.append((genre, round(total / count, 2), count))

    return sorted(stats, key=lambda x: x[1], reverse=True)


def sort_movies(movies, sort_key, reverse=False):
    if sort_key not in ["title", "year", "rating"]:
        return movies

    return sorted(movies, key=lambda m: m[sort_key], reverse=reverse)


# -------------------------------
# ADVANCED FUNCTIONS
# -------------------------------

def build_genre_catalog(movies):
    catalog = {}

    for movie in movies:
        primary = movie["genres"][0]

        if primary in catalog:
            catalog[primary].append(movie)
        else:
            catalog[primary] = [movie]

    return catalog


def display_genre_catalog(catalog):
    print("\n===== Genre Catalog =====")

    for genre, movie_list in catalog.items():
        print(f"\n{genre}")

        ordered = sorted(movie_list, key=lambda m: m["rating"], reverse=True)

        for movie in ordered:
            print(f"  {movie['title']} ({movie['rating']})")


def get_rating_lookup(movies):
    return {movie["title"]: movie["rating"] for movie in movies}


def find_genre_champions(catalog):
    champions = {}

    for genre, movie_list in catalog.items():
        best = movie_list[0]

        for movie in movie_list:
            if movie["rating"] > best["rating"]:
                best = movie

        champions[genre] = best["title"]

    return champions


def load_from_csv(filename):
    try:
        movies = []

        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            next(reader, None)

            for row in reader:
                movies.append({
                    "title": row[0],
                    "year": int(row[1]),
                    "genres": row[2].split("|"),
                    "rating": float(row[3])
                })

        return movies

    except FileNotFoundError:
        return get_starter_movies()


def save_to_csv(movies, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["title", "year", "genres", "rating"])

        for movie in movies:
            writer.writerow([
                movie["title"],
                movie["year"],
                "|".join(movie["genres"]),
                movie["rating"]
            ])


# -------------------------------
# MAIN PROGRAM
# -------------------------------

def main():
    FILE = os.path.join(os.path.dirname(__file__), "movies.csv")

    movies = load_from_csv(FILE)

    display_movies(movies, "Your Movie Collection")

    # Add 2 movies
    for i in range(2):
        print(f"\nAdd Movie {i+1}")

        title = input("Title: ")

        while True:
            try:
                year = int(input("Year: "))
                break
            except ValueError:
                print("Enter a valid year.")

        genres = [
            g.strip()
            for g in input("Genres (comma separated): ").split(",")
        ]

        while True:
            try:
                rating = float(input("Rating: "))
                break
            except ValueError:
                print("Enter a valid rating.")

        movies.append(create_movie(title, year, genres, rating))

    movies.sort(key=lambda m: m["year"])
    display_movies(movies, "All Movies Sorted by Year")

    display_movies(find_top_rated(movies, 3), "Top 3 Rated Movies")

    print("\nCollection average rating:", get_average_rating(movies))

    # Unique genres
    unique = []

    for movie in movies:
        for genre in movie["genres"]:
            if genre not in unique:
                unique.append(genre)

    print("\nGenres:", sorted(unique))

    # Genre catalog
    catalog = build_genre_catalog(movies)
    display_genre_catalog(catalog)

    # Rating lookup
    lookup = get_rating_lookup(movies)

    title = input("\nLookup movie rating: ")

    if title in lookup:
        print("Rating:", lookup[title])
    else:
        print("Movie not found.")

    # Genre champions
    print("\n===== Genre Champions =====")
    champions = find_genre_champions(catalog)

    for genre, title in champions.items():
        print(f"{genre} → {title}")

    # FILTER
    genre = input("\nFilter by genre: ")
    filtered = filter_by_genre(movies, genre)

    if filtered:
        display_movies(filtered, f"Movies in {genre}")
    else:
        print("No matching movies found.")

    # UPDATE
    choice = input("\nUpdate a rating? (y/n): ").lower()

    if choice == "y":
        t = input("Movie title: ")
        r = float(input("New rating: "))

        if update_rating(movies, t, r):
            print("Rating updated.")
            display_movies(movies, "Updated Collection")
        else:
            print("Movie not found.")

    # STATS
    print("\n===== Genre Statistics =====")
    stats = get_genre_stats(movies)

    print(f"{'Genre':15}{'Avg':10}{'Count'}")

    for g, avg, count in stats:
        print(f"{g:15}{avg:<10}{count}")

    # SORT OPTIONS
    sort_key = input("\nSort by (title/year/rating): ")
    desc = input("Descending? (y/n): ").lower()

    sorted_movies = sort_movies(movies, sort_key, desc == "y")

    display_movies(sorted_movies, "Custom Sort")

    # SAVE
    save_to_csv(movies, FILE)
    print(f"\nSaved {len(movies)} movies to CSV.")


main()