import csv
from pathlib import Path


TARGET_SITES = "mercari;yahoo"
KEYWORD_TRANSLATIONS = {
    "jacket": "ジャケット",
    "gloves": "グローブ",
    "boots": "ブーツ",
    "hoodie": "パーカー",
    "pants": "パンツ",
    "t-shirt": "Tシャツ",
    "shirt": "シャツ",
    "cap": "キャップ",
    "hat": "帽子",
}
BRAND_TRANSLATIONS = {
    "Dainese": "ダイネーゼ",
}


def load_ebay_candidates(csv_path):
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def format_request_id(index):
    return f"{index:03d}"


def build_search_keyword(title):
    # Manusへ渡す検索語は、ブランド名を残しつつ主要な商品種別を日本語化する。
    words = title.split()
    translated_words = []

    for word in words:
        clean_word = word.strip()
        lower_word = clean_word.lower()
        translated_words.append(
            BRAND_TRANSLATIONS.get(
                clean_word,
                KEYWORD_TRANSLATIONS.get(lower_word, clean_word),
            )
        )

    return " ".join(translated_words)


def build_manus_requests(candidates):
    requests = []

    for index, candidate in enumerate(candidates, start=1):
        title = candidate["title"]
        requests.append(
            {
                "request_id": format_request_id(index),
                "title": title,
                "search_keyword": build_search_keyword(title),
                "target_sites": TARGET_SITES,
                "ebay_price_jpy": candidate["ebay_price_jpy"],
                "ebay_url": candidate["ebay_url"],
            }
        )

    return requests


def save_manus_requests(requests, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "request_id",
        "title",
        "search_keyword",
        "target_sites",
        "ebay_price_jpy",
        "ebay_url",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(requests)


def generate_manus_request_file(input_path, output_path):
    candidates = load_ebay_candidates(input_path)
    requests = build_manus_requests(candidates)
    save_manus_requests(requests, output_path)
    return requests


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "data" / "ebay_raw" / "ebay_candidates.csv"
    output_path = project_root / "data" / "manus_requests" / "manus_request.csv"
    requests = generate_manus_request_file(input_path, output_path)
    print(f"Manus依頼CSVを作成しました: {output_path}")
    print(f"依頼件数: {len(requests)}件")


if __name__ == "__main__":
    main()
