import csv
import sys

from sites import craigslist, youtube

LISTINGS_FILE = "listings.csv"

# Maps a listings.csv "site" value to the module that knows how to post it.
# Add a new sites/<name>.py with a post(data) function, then register it
# here to wire it into the runner.
POSTERS = {
    "craigslist": craigslist.post,
    "youtube": youtube.post,
}


def load_listings(path=LISTINGS_FILE):
    with open(path, newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("title")]


def choose_listing(listings):
    print("\nListings in", LISTINGS_FILE + ":")
    for i, listing in enumerate(listings, start=1):
        site = (listing.get("site") or "craigslist").strip()
        post_date = listing.get("post_date", "").strip() or "no date set"
        print(f"  {i}. [{site}] {listing['title']} (${listing['price']}) - {post_date}")
    while True:
        choice = input(f"Pick a listing to post (1-{len(listings)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(listings):
            return listings[int(choice) - 1]
        print("Invalid choice, try again.")


def post_listing(data):
    site = (data.get("site") or "craigslist").strip().lower()
    poster = POSTERS.get(site)
    if poster is None:
        print(f"Skipping '{data.get('title', '<untitled>')}': unknown site '{site}' (no sites/{site}.py).")
        return
    poster(data)


if __name__ == "__main__":
    try:
        listings = load_listings()
    except FileNotFoundError:
        print(f"{LISTINGS_FILE} not found. Copy listings.example.csv to {LISTINGS_FILE} and fill in your info.")
        sys.exit(1)

    if not listings:
        print(f"No listings found in {LISTINGS_FILE}. Add a row and try again.")
        sys.exit(1)

    chosen = listings[0] if len(listings) == 1 else choose_listing(listings)
    post_listing(chosen)
