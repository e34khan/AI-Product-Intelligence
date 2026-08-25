"""
Stream the Electronics metadata file directly over HTTP (instead of via the
`datasets` library's loading script, which no longer works on current `datasets`
versions and would require executing arbitrary remote code anyway) and collect
a handful of laptop-looking products with enough reviews to be useful.
"""

import gzip
import json

import requests

METADATA_URL = (
    "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/"
    "raw/meta_categories/meta_Electronics.jsonl.gz"
)

MAX_CANDIDATES = 30
MIN_RATING_COUNT = 50  # skip products with too few ratings to be a useful review source


def looks_like_laptop(item: dict) -> bool:
    categories = [c.lower() for c in (item.get("categories") or [])]
    return "laptops" in categories


def find_candidates() -> list[dict]:
    response = requests.get(METADATA_URL, stream=True)
    response.raise_for_status()

    candidates = []
    # the file is gzip-compressed JSON-lines (one JSON object per line);
    # GzipFile decompresses the streamed bytes as they arrive, so we never
    # hold the full ~1.3GB (compressed) file in memory or on disk
    with gzip.GzipFile(fileobj=response.raw) as f:
        for line in f:
            item = json.loads(line)

            if not looks_like_laptop(item):
                continue

            rating_number = item.get("rating_number") or 0
            if rating_number < MIN_RATING_COUNT:
                continue

            candidates.append({
                "parent_asin": item.get("parent_asin"),
                "title": item.get("title"),
                "average_rating": item.get("average_rating"),
                "rating_number": rating_number,
            })

            if len(candidates) >= MAX_CANDIDATES:
                break  # stop pulling from the stream once we have enough

    return candidates


if __name__ == "__main__":
    for candidate in find_candidates():
        print(candidate)
