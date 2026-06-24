import csv
from pathlib import Path


MIN_EBAY_PRICE_JPY = 15000
PRIORITY_KEYWORDS = [
    "KTM",
    "PowerWear",
    "PowerParts",
    "Dainese",
    "Alpinestars",
    "Ignition",
    "Motorhelix",
    "HPI",
    "Nismo",
    "Skyline",
    "GT-R",
]


def load_candidates(input_path):
    with input_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def parse_int(value):
    if value in (None, ""):
        return 0
    return int(float(value))


def contains_priority_keyword(title):
    lower_title = title.lower()
    return any(keyword.lower() in lower_title for keyword in PRIORITY_KEYWORDS)


def select_top_candidates(candidates, limit=20):
    filtered_candidates = [
        candidate
        for candidate in candidates
        if parse_int(candidate["ebay_price_jpy"]) > MIN_EBAY_PRICE_JPY
        and contains_priority_keyword(candidate["title"])
    ]
    filtered_candidates.sort(
        key=lambda candidate: parse_int(candidate["ebay_price_jpy"]),
        reverse=True,
    )

    top_candidates = []
    for rank, candidate in enumerate(filtered_candidates[:limit], start=1):
        top_candidates.append(
            {
                "rank": rank,
                "title": candidate["title"],
                "ebay_price_jpy": candidate["ebay_price_jpy"],
                "ebay_url": candidate["ebay_url"],
            }
        )

    return top_candidates


def save_top_candidates(candidates, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["rank", "title", "ebay_price_jpy", "ebay_url"]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(candidates)


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = (
        project_root / "data" / "manus_requests" / "ebay_candidates_for_manus.csv"
    )
    output_path = project_root / "data" / "processed" / "top20_candidates.csv"

    candidates = load_candidates(input_path)
    top_candidates = select_top_candidates(candidates)
    save_top_candidates(top_candidates, output_path)

    print(f"上位候補CSVを作成しました: {output_path}")
    print(f"候補件数: {len(top_candidates)}件")


if __name__ == "__main__":
    main()
