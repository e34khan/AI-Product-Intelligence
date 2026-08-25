"""
Stream the Electronics metadata file and print the full record for a specific
set of parent_asins, so we can compare fields between a real laptop and a
laptop accessory that our substring filter incorrectly matched.
"""

import gzip
import json

import requests

METADATA_URL = (
    "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/"
    "raw/meta_categories/meta_Electronics.jsonl.gz"
)

TARGET_ASINS = {"B0822SL7JX", "B077BNJHVJ"}


def main() -> None:
    response = requests.get(METADATA_URL, stream=True)
    response.raise_for_status()

    found = {}
    with gzip.GzipFile(fileobj=response.raw) as f:
        for line in f:
            item = json.loads(line)
            asin = item.get("parent_asin")
            if asin in TARGET_ASINS:
                found[asin] = item
            if len(found) == len(TARGET_ASINS):
                break

    for asin, item in found.items():
        print(f"--- {asin} ---")
        print(f"title: {item.get('title')}")
        print(f"main_category: {item.get('main_category')}")
        print(f"categories: {item.get('categories')}")
        print()


if __name__ == "__main__":
    main()
