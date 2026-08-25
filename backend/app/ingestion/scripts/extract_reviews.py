"""
Stream the full Electronics reviews file and pull out every
review belonging to 5 chosen laptop products, saving them to a local file.
This is a full scan so we can't stop early
because matching reviews could be anywhere in the file.
"""

import gzip
import json

import requests

REVIEWS_URL = (
    "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/"
    "raw/review_categories/Electronics.jsonl.gz"
)

TARGET_ASINS = {
    "B08157248B",  # 2019 MacBook Air (Renewed)
    "B01GO1T2TS",  # HP 15.6" budget laptop
    "B076DKFYF9",  # Dell Latitude E7450
    "B0BY2Y5T1J",  # ASUS ROG Strix G15
    "B09H5Z36S1",  # Microsoft Surface Laptop Studio
}

OUTPUT_PATH = "backend/app/ingestion/data/laptop_reviews.jsonl"
PROGRESS_EVERY = 500_000  # print a progress line every N lines scanned


def main() -> None:
    response = requests.get(REVIEWS_URL, stream=True)
    response.raise_for_status()

    matched = 0
    scanned = 0

    with gzip.GzipFile(fileobj=response.raw) as f, open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        for line in f:
            scanned += 1

            item = json.loads(line)
            if item.get("parent_asin") in TARGET_ASINS:
                out.write(line if isinstance(line, str) else line.decode("utf-8"))
                matched += 1

            if scanned % PROGRESS_EVERY == 0:
                print(f"scanned={scanned:,} matched={matched}", flush=True)

    print(f"done. scanned={scanned:,} matched={matched}")


if __name__ == "__main__":
    main()
